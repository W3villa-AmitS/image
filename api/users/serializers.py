import re
import jwt

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.conf import settings

from django.utils import timezone
from django.utils.six import text_type
from django.db.utils import IntegrityError

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable, PermissionDenied

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.settings import api_settings

from .tokens import CustomisedRefreshToken

from .models import Request, UserInformation
from .random_code import get_uuid_8

#
# Helper functions
#
def lowest_precedence_role(possibleRoles):
    """
    Todo:
    :param possibleRoles:
    :return:
    """
    for presedence_role in "WSMA":
        for assigned_role in possibleRoles:
            if assigned_role == presedence_role:
                return assigned_role

def phone_number(value):
    """
    Todo:
    :param value:
    :return:
    """
    if (not len(value) == 12) or (re.search("[^0-9]", value)):    # country code(2) + phone number(10)
        raise serializers.ValidationError("Invalid phone number '%s'."% value)

def gender(value):
    """
    Todo:
    :param value:
    :return:
    """
    valid_values = ("M", "F", "T")
    if value not in valid_values:
        raise serializers.ValidationError(r"Invalid gender '%s' specified.\nValid values are '%s'" % (value, ', '.join(valid_values)))

def roles(value):
    """
    Validate the specified string.
    :param value: string to be validated
    :exception ValidationError: string is not in csv format.
    """
    if len(value) > 4:
        raise serializers.ValidationError("Invalid role type specified.")
    for char in value:
        if not char in ('A', 'M', 'S', 'W'):
            raise serializers.ValidationError("Invalid role type specified.")


class CustomizedObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # check if user is in active state to login
        if not user.state == 'A':
            try:
                state = {'D': 'deactivated', 'U': 'uninitialized', 'L': 'locked'}[user.state]
            except KeyError:
                raise PermissionDenied(detail="Unable to determine the state of user.")

            raise PermissionDenied(detail="Unable to login user in state '%s'"% state)

        # check if password is too old to login
        delta = timedelta(days = int(settings.PASSWORD_MANAGEMENT_PARAMETERS.get('maximum_age', '90')))
        if (timezone.now() - user.password_set_at) >= delta:
            raise PermissionDenied(detail="Password expired. Please reset your password.")

        token = super(CustomizedObtainPairSerializer, cls).get_token(user)

        token['username']   = user.username
        token['roles']      = user.roles

        user_object = get_user_model().objects.get(pk=int(user.id))

        # Use the last active role by default
        # For first time login assign the lowest precedence role
        active_role = user_object.active_role
        if not active_role:
            active_role = lowest_precedence_role(user.roles)
            user_object.active_role = active_role
            user_object.save()

        token['active_role'] = active_role

        return token

class CustomizedTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        refresh = CustomisedRefreshToken(attrs['refresh'])

        data = {'access': text_type(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data['refresh'] = text_type(refresh)

        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    roles    = serializers.CharField(max_length=4, validators=[roles])  # 'ASMW' every character represents a role


    def validate_password(self, value):
        errors = dict()
        try:
            password_validation.validate_password(value)
        except ValidationError as exc:
            errors['password'] = list(exc.messages)

        if errors:
            raise serializers.ValidationError(str(errors))

        return value


    def create(self, validated_data):
        user = get_user_model().objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            state = validated_data['state'],
            roles = validated_data['roles'],
            password_set_at = timezone.now()
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'email', 'state', 'roles']


class RoleSerializer(serializers.Serializer):
    role_types = (
        ("admin"    , "A"),
        ("manager"  , "M"),
        ("searcher" , "S"),
        ("worker"   , "W"),
    )
    role = serializers.ChoiceField(choices=role_types)

    def update(self, instance, validated_data):

        switch_to_role = dict(RoleSerializer.role_types)[validated_data['role']]

        if switch_to_role in instance.roles:
            instance.active_role = switch_to_role
            instance.save()
        else:
            raise NotAcceptable(detail="User is not eligible for the role of '%s'" % validated_data['role'])


class CustomizedTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        super(CustomizedTokenVerifySerializer, self).validate(attrs)
        payload = jwt.decode(attrs['token'], verify=False)
        return payload


class RequestSerializer(serializers.Serializer):
    email_id     = serializers.EmailField()
    request_type = serializers.ChoiceField(choices=('new', 'reset'))

    def create(self, validated_data):
        user_model = get_user_model()

        if validated_data['request_type'] == 'new':
            # check if there is already a user registered with specified credentials
            try:
                user_model.objects.get(email=validated_data['email_id'])
                raise PermissionDenied(detail="User with email '%s' is already registered." % validated_data['email_id'])
            except user_model.DoesNotExist:
                pass

        elif validated_data['request_type'] == 'reset':
            # check if a user registered with specified credentials
            try:
                user_model.objects.get(email=validated_data['email_id'])
            except user_model.DoesNotExist:
                raise PermissionDenied(detail="User with email '%s' is not registered." % validated_data['email_id'])

        else:
            raise NotAcceptable(detail="Unknown request type '%s'" % validated_data['request_type'])

        try:
            registration_request = Request.objects.get(email_id=validated_data['email_id'])
        except Request.DoesNotExist:
            registration_request = Request.objects.create( email_id   = validated_data['email_id'], 
                                                           created_at = timezone.now())

        secret_key = get_uuid_8()
        registration_request.secret_key = make_password(secret_key)
        registration_request.save()

        return secret_key


class RegistrationSerializer(serializers.ModelSerializer):
    email_id            = serializers.EmailField (required=True, allow_blank=False)
    verification_code   = serializers.CharField  (required=True, allow_blank=False, max_length=8)
    username            = serializers.CharField  (required=True, allow_blank=False, max_length=12)
    firstname           = serializers.CharField  (required=True, allow_blank=False, max_length=20)
    lastname            = serializers.CharField  (required=True, allow_blank=False, max_length=20)
    date_of_birth       = serializers.DateField  (required=True, format="%Y/%m/%d")
    gender              = serializers.CharField  (required=True, allow_blank=False, max_length=1,  validators=[gender])
    phone_number        = serializers.CharField  (required=True, allow_blank=False, max_length=12, validators=[phone_number])
    location            = serializers.CharField  (required=True, allow_blank=False, max_length=50)
    password            = serializers.CharField  (required=True, style={'input_type': 'password'}, write_only=True)

    def validate_password(self, value):
        errors = dict()
        try:
            password_validation.validate_password(value)
        except ValidationError as exc:
            errors['password'] = list(exc.messages)

        if errors:
            raise serializers.ValidationError(str(errors))

        return value

    def create(self, validated_data):
        #
        # 1. check combination of verification code and email
        #
        try:
            request = Request.objects.get( email_id = validated_data['email_id'])
        except Request.DoesNotExist:
            raise PermissionDenied(detail="No such request registered.")

        #
        # 2. check for the expiration of the verification code
        #
        try:
            delta = settings.OTP_EXPIRATION
        except:
            delta = '24'

        delta = timedelta(hours=int(delta))
        if timezone.now() > (request.created_at + delta):
            # request.delete()
            raise PermissionDenied(detail="Verification code expired. Please fetch a new verification code.")

        #
        # 3. validate the verification code
        #
        if not check_password(validated_data['verification_code'], request.secret_key):
            raise PermissionDenied(detail="Invalid verification code.")

        #
        # 4. check if there is already a user registered with specified credentials
        #
        user_model = get_user_model()
        try:
            user_model.objects.get(email=validated_data['email_id'])
            raise PermissionDenied(detail="Email '%s' is already used for registration." % validated_data['email_id'])
        except user_model.DoesNotExist:
            pass

        try:
            # 5. create an object of User Model (set roles as 'W')
            #
            user = user_model.objects.create( username = validated_data['username'],
                                              email    = validated_data['email_id'],
                                              state    = 'A', roles = 'W',
                                              password_set_at = timezone.now())
            user.set_password(validated_data['password'])
            user.save()
        except IntegrityError:
            raise PermissionDenied(detail="Username '%s' is already in use." % validated_data['username'])

        #
        # 6. create an object of User Information Model
        #
        UserInformation.objects.create( user_id = user,  first_name = validated_data['firstname'],
                                        last_name     = validated_data['lastname'],
                                        date_of_birth = validated_data['date_of_birth'],
                                        phone_number  = validated_data['phone_number'],
                                        location      = validated_data['location'],
                                        gender        = validated_data['gender'])


        #
        # 7. remove entry from Request table
        #
        request.delete()

        return user

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email_id', 'firstname', 'lastname', 'date_of_birth', 'phone_number', 'location', 'gender', 'verification_code', 'password']


class ResetPasswordSerializer(serializers.Serializer):
    email_id            = serializers.EmailField(required=True)
    verification_code   = serializers.CharField (required=True, max_length=8)
    password            = serializers.CharField (required=True, style={'input_type': 'password'}, write_only=True)

    def validate_password(self, value):
        errors = dict()
        try:
            password_validation.validate_password(value)
        except ValidationError as exc:
            errors['password'] = list(exc.messages)

        if errors:
            raise serializers.ValidationError(str(errors))

        return value

    def update(self, instance, validated_data):
        #
        # 1. check combination of verification code and email
        #
        try:
            request = Request.objects.get( email_id = validated_data['email_id'])
        except Request.DoesNotExist:
            raise PermissionDenied(detail="No request registered for this user.")

        #
        # 2. check for the expiration of the verification code
        #
        try:
            delta = settings.OTP_EXPIRATION
        except:
            delta = '24'

        delta = timedelta(hours=int(delta))
        if timezone.now() > (request.created_at + delta):
            # request.delete()
            raise PermissionDenied(detail="Verification code expired. Please fetch a new verification code.")

        #
        # 3. validate the verification code
        #
        if not check_password(validated_data['verification_code'], request.secret_key):
            raise PermissionDenied(detail="Invalid verification code.")

        #
        # 4. Check if the new password is same as used before
        #
        old_passwords = instance.last_passwords[:]
        for pwd in old_passwords:
            if check_password(validated_data['password'], pwd):
                raise PermissionDenied(detail="The value provided for the new password does not meet the history requirements.")

        if len(old_passwords) >= 4:
            old_passwords = old_passwords[1:4]        
        old_passwords.append(make_password(validated_data['password']))

        #
        # 5. check if password is getting a reset too early
        #
        delta = timedelta(days = int(settings.PASSWORD_MANAGEMENT_PARAMETERS.get('minimum_age', '1')))
        if (timezone.now() - instance.password_set_at) < delta:
            raise PermissionDenied(detail="Password is not old enough to reset.")

        #
        # 6. update password
        #
        instance.set_password(validated_data['password'])
        instance.last_passwords = old_passwords
        instance.password_set_at = timezone.now()
        instance.save()

        #
        # 7. remove entry from Request table
        #
        request.delete()

        return instance


class SystemEmailSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True, max_length=255)
    body    = serializers.CharField(required=True, max_length=1023)


class UserCreationSerializer(serializers.Serializer):
    email_id            = serializers.EmailField(required=True)
    username            = serializers.CharField (required=True, max_length=12)
    firstname           = serializers.CharField (required=True, max_length=20)
    lastname            = serializers.CharField (required=True, max_length=20)
    roles               = serializers.CharField (required=True, max_length=4, validators=[roles])
    date_of_birth       = serializers.DateField (required=True, format="%Y/%m/%d")
    gender              = serializers.CharField (required=True, max_length=1,  validators=[gender])
    phone_number        = serializers.CharField (required=True, max_length=12, validators=[phone_number])
    location            = serializers.CharField (required=True, max_length=50)

    def create(self, validated_data):

        #
        # 1. check if there is already a user registered with specified email
        #
        user_model = get_user_model()
        try:
            user_model.objects.get(email=validated_data['email_id'])
            raise PermissionDenied(detail="Email '%s' is already used for registration." % validated_data['email_id'])
        except user_model.DoesNotExist:
            pass

        #
        # 2. check if there is already a user registered with specified username
        #
        try:
            user_model.objects.get(username=validated_data['username'])
            raise PermissionDenied(detail="Username '%s' is already used for registration." % validated_data['username'])
        except user_model.DoesNotExist:
            pass


        # 3. create an object of User Model
        #
        user = user_model.objects.create( username = validated_data['username'],
                                          email    = validated_data['email_id'],
                                          state    = 'A',
                                          roles    = validated_data['roles'],
                                          password_set_at = timezone.now())


        #
        # 4. create an object of User Information Model
        #
        UserInformation.objects.create( user_id = user,  first_name = validated_data['firstname'],
                                        last_name     = validated_data['lastname'],
                                        date_of_birth = validated_data['date_of_birth'],
                                        phone_number  = validated_data['phone_number'],
                                        location      = validated_data['location'],
                                        gender        = validated_data['gender'])

        return {"username": validated_data['username'], "email_id": validated_data['email_id'] }
