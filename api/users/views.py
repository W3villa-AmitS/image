from mako.template import Template

from django.conf import settings

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, PermissionDenied

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from rest_condition import And, Or

from .models import User
from .serializers import CustomizedObtainPairSerializer, CustomizedTokenRefreshSerializer
from .serializers import CustomizedTokenVerifySerializer
from .serializers import UserSerializer, RoleSerializer
from .serializers import RequestSerializer, RegistrationSerializer, ResetPasswordSerializer
from .serializers import SystemEmailSerializer
from .serializers import UserCreationSerializer

from .utilities import send_email

from .permissions import IsAdmin, IsManager, IsSearcher
from .prevent import UserLoginRateThrottle


#
# helper functions
#
def _role(roles):
    result = []
    for k in roles:
        result.append({'A': 'admin',
                       'M': 'manager',
                       'S': 'searcher',
                       'W': 'worker'}[k])
    return result


def _state(status):
    return { 'A': 'active',
             'D': 'deactivated'}[status]


class CustomizedTokenObtainPairView(TokenObtainPairView):
    """
    Accepts username and password credentials from user and returns an access and refresh JSON web\
    token pair to prove the authentication of those credentials.
    """
    serializer_class = CustomizedObtainPairSerializer

    # Add throttling for production environment
    if not settings.DEBUG:
        throttle_classes = (UserLoginRateThrottle,)


class CustomisedTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = CustomizedTokenRefreshSerializer


#
# https://stackoverflow.com/questions/35970970/django-rest-framework-permission-classes-of-viewset-method
#
class UserViewSet(viewsets.ModelViewSet):
    """
    create:
    Create a new User.
    * Requires token authentication.
    * Only admin users are able to access this view.

    list:
    Return a list of all existing users.
    * Requires token authentication.
    * Only manager users are able to access this view.

    retrieve:
    Return the details of the given user.
    * Requires token authentication.
    * Only manager users are able to access this view.

    update:
    Update the user detials.
    * Requires token authentication.
    * Only admin users are able to access this view.

    partial_update:
    Update the user details partially.
    * Requires token authentication.
    * Only admin users are able to access this view.

    destroy:
    Delete a user.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    permission_classes_by_action = {
        'create'                :   [And(IsAuthenticated, IsAdmin), ],                  # post
        'list'                  :   [And(IsAuthenticated, Or(IsAdmin, IsManager)), ],   # get
        'retrieve'              :   [And(IsAuthenticated, Or(IsAdmin, IsManager)), ],   # get
        'user_activation'       :   [And(IsAuthenticated, IsAdmin), ],                  # post
        'user_deactivation'     :   [And(IsAuthenticated, IsAdmin), ],                  # post
    }

    def create(self, request, *args, **kwargs):
        return super(UserViewSet, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        all_users = User.objects.all()

        #
        # filter on status if query string specified
        #
        if request.GET:
            if 'status' in request.GET:

                if len(dict(request.GET)['status']) > 1:
                    return Response({"error": "query for multiple status values is not allowed."}, status=status.HTTP_400_BAD_REQUEST)

                status_enquired = dict(request.GET)['status'][0]
                if status_enquired in ['activated', 'deactivated']:
                    filtered_users = [user for user in all_users if user.state == {'activated': 'A', 'deactivated': 'D'}[status_enquired]]
                else:
                    return Response({"error": "invalid status type '%s' specified."%status_enquired}, status=status.HTTP_400_BAD_REQUEST)
            all_users = filtered_users

        serializer = UserSerializer(instance=all_users, many=True)
        allowed_fields = ["id", "username", "state", "roles"]

        filtered_data = [{key:val for key, val in elem.items() if key in allowed_fields} for elem in serializer.data]

        for elem in filtered_data:
            elem['roles'] = _role(elem['roles'])
            elem['state'] = _state(elem['state'])

        return Response(filtered_data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            elem = User.objects.get(id=int(pk))
        except User.DoesNotExist:
            return Response({"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        result = dict()
        result['id']       = elem.id
        result['username'] = elem.username
        result['state']    = _state(elem.state)
        result['roles']    = _role(elem.roles)

        return Response(result)

    @action(methods=['post'], detail=True, url_path='activate', url_name='user_activation')
    def user_activation(self, request, pk=None, *args, **kwargs):
        try:
            user = User.objects.get(id=int(pk))
        except User.DoesNotExist:
            return Response({"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # activate the user
        if user.state == 'D':
            user.state = 'A'
            user.save()

            return Response(status=status.HTTP_200_OK)
        return Response({"error": "Can't activate a user in state other than 'Deactivated'"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='deactivate', url_name='user_deactivation')
    def user_deactivation(self, request, pk=None, *args, **kwargs):
        try:
            user = User.objects.get(id=int(pk))
        except User.DoesNotExist:
            return Response({"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # disallow the deactivation of a user with Admin role
        if 'A' in user.roles:
            Response({"error": "Can't deactivate a user with 'Admin' role."}, status=status.HTTP_400_BAD_REQUEST)

        # deactivate the user
        if user.state == 'A':
            user.state = 'D'
            user.save()

            return Response(status=status.HTTP_200_OK)
        return Response({"error": "Can't deactivate a user in state other than 'Activated'"}, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    #
    # unsupported actions
    #
    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)


class SwitchRoleView(APIView):
    """
    Accepts role as a string to which user is willing to switch.
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            user = User.objects.get(pk=int(request.user.id))
        except User.DoesNotExist:
            return Response({"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleSerializer(data=request.data, instance=user)

        if serializer.is_valid():
            try:
                serializer.update(user, serializer.validated_data)
            except NotAcceptable as err:
                return Response({'error': err.detail}, status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomisedTokenVerifyView(TokenVerifyView):
    """
    Takes a token and validate it. On success return the paylaod of the token.
    """
    serializer_class = CustomizedTokenVerifySerializer


class RequestView(APIView):
    """
    Accepts a request and return unique key for the user to register
    """
    def post(self, request):
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                secret_key = serializer.create(serializer.validated_data)
            except PermissionDenied as err:
                # return Response({'error': str(err)}, status=status.HTTP_406_NOT_ACCEPTABLE)

                #
                # in order to avoid detection at login, the invalid requests to be reported by email
                #
                reason = '%s' % {'new'  : 'register a new user',
                                 'reset': 'reset password'}[serializer.validated_data['request_type']]

                email_subject = "Image Factory - Illegal attempt to %s is detected !" % reason
                email_template = Template(filename=r'./users/templates/invalid_request_email.mako')
                email_body = email_template.render(email_id = serializer.validated_data['email_id'], reason=reason)
                send_email(email_subject, email_body, [serializer.validated_data['email_id']])

                return Response(status=status.HTTP_201_CREATED)

            except Exception as err:
                return Response({'error': err.args[0]}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data['request_type'] == 'new':
            email_template = Template(filename=r'./users/templates/new_registration_request_email.mako')
            email_subject  = "Welcome to ImageFactory!"
        elif serializer.validated_data['request_type'] == 'reset':
            email_template = Template(filename=r'./users/templates/password_reset_email.mako')
            email_subject = "ImageFactory - Password Reset"
        else:
            return Response({'error': 'Invalid request_type specified'}, status=status.HTTP_400_BAD_REQUEST)

        #
        # send an email
        #
        email_body     = email_template.render( email_id = serializer.validated_data['email_id'],
                                                key      = secret_key)

        try:
            send_email(email_subject, email_body, [serializer.validated_data['email_id']])
        except AssertionError as err:
            return Response({'error': err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class RegistrationView(APIView):
    """
    Validate the credentials required for registration and register a user as worker
    """
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.create(serializer.validated_data)
            except PermissionDenied as err:
                return Response({'error': "%s" % err}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class ResetPasswordView(APIView):
    """
    Validate the credentials required for password reset and reset the password
    """
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email_id'])
            except User.DoesNotExist:
                return Response({'error': "User with email id '%s' is not registered." \
                                          % serializer.validated_data['email_id']}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                serializer.update(user, serializer.validated_data)
            except PermissionDenied as err:
                return Response({'error': "%s" % err}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class SystemEmailView(APIView):
    """
    Send an email to application maintainers.
    """
    permission_classes = (IsAuthenticated, IsAdmin)

    def post(self, request):
        serializer = SystemEmailSerializer(data=request.data)

        if serializer.is_valid():
            #
            # send an email
            #
            email_subject = serializer.validated_data['subject']
            email_body    = serializer.validated_data['body']

            try :
                recipients = settings.SYSTEM_EMAIL_RECIPIENTS
            except:
                return Response({'error': 'System email recipients not listed.'}, status=status.HTTP_200_OK)

            try:
                send_email(email_subject, email_body, recipients)
            except AssertionError as err:
                return Response({'error': err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreationView(APIView):
    """
    Create a user with all user details.
    """
    permission_classes = (IsAuthenticated, IsAdmin)

    def post(self, request):
        serializer = UserCreationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user_details = serializer.create(serializer.validated_data)
            except PermissionDenied as err:
                return Response({'error': "%s" % err}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #
        # send an intimation email
        #
        email_template = Template(filename=r'./users/templates/new_user_intimation_of_account_creation_email.mako')
        email_subject  = "Welcome to ImageFactory!"

        email_body  = email_template.render( email_id  = serializer.validated_data['email_id'],
                                             username  = serializer.validated_data['username'],
                                             firstname = serializer.validated_data['firstname'],
                                             lastname  = serializer.validated_data['lastname']
                                             )

        try:
            send_email(email_subject, email_body, [serializer.validated_data['email_id']])
        except AssertionError as err:
            return Response({'error': err.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(user_details, status=status.HTTP_201_CREATED)
