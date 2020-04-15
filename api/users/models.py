import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class User(AbstractUser):
    state_types = (
        ('U', 'Uninitialized'),
        ('L', 'Locked'),
        ('A', 'Activated'),
        ('D', 'Deactivated'),
    )

    role_types = (
        ('A', 'Admin'),
        ('M', 'Manager'),
        ('S', 'Searcher'),
        ('W', 'Worker'),
    )
    id              = models.AutoField      (primary_key=True)
    username        = models.CharField      (db_index=True, max_length=255, unique=True)
    email           = models.EmailField     (db_index=True, unique=True)
    state           = models.CharField      (max_length=1, choices=state_types)
    roles           = models.CharField      (max_length=4) # 'ASMW' every character represents a role
    active_role     = models.CharField      (max_length=1, choices=role_types)
    created_at      = models.DateTimeField  (auto_now_add=True )
    updated_at      = models.DateTimeField  (auto_now=True)

    jwt_secret      = models.UUIDField      (default=uuid.uuid4)

    last_passwords  = ArrayField(base_field=models.CharField(max_length=128), default=list)
    password_set_at = models.DateTimeField ()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


def jwt_get_secret_key(user_model):
    return user_model.jwt_secret

#
#
# ToDo: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
#
# from django.db import models
# from django.contrib.auth.models import PermissionsMixin
# from django.contrib.auth.base_user import AbstractBaseUser
# from django.utils.translation import ugettext_lazy as _
#
# from .managers import UserManager
#
# class User(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(_('email address'), unique=True)
#     first_name = models.CharField(_('first name'), max_length=30, blank=True)
#     last_name = models.CharField(_('last name'), max_length=30, blank=True)
#     date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
#     is_active = models.BooleanField(_('active'), default=True)
#     avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')
#
#     def get_full_name(self):
#         '''
#         Returns the first_name plus the last_name, with a space in between.
#         '''
#         full_name = '%s %s' % (self.first_name, self.last_name)
#         return full_name.strip()
#
#     def get_short_name(self):
#         '''
#         Returns the short name for the user.
#         '''
#         return self.first_name


class UserInformation(models.Model):
    """
    Defines the model for storing user information. It is mainly used to check if the user fulfills
    the job criteria set by Searcher.
    """
    gender = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('T', 'Transgender')
    )
    user_id       = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    first_name    = models.CharField(max_length=50)
    last_name     = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    phone_number  = models.CharField(max_length=12)
    location      = models.CharField(max_length=30)
    gender        = models.CharField(max_length=1, choices=gender)


class Worker(models.Model):
    """
    Model to store information specific to worker.
    """
    # TODO add validation to current task to check if value is valid
    user_id           = models.IntegerField(unique=False)
    is_active         = models.BooleanField(default=True)
    is_completed      = models.BooleanField(default=False)
    job_id            = models.CharField(max_length=8)
    qat_passed        = models.IntegerField(default=0)
    qat_failed        = models.IntegerField(default=0)
    task_allocated    = models.CharField(max_length=24)
    tasks_completed   = ArrayField(base_field=models.CharField(max_length=24), default=list)
    disqualified_till = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('user_id', 'job_id'),)


class TaskCompleted(models.Model):
    """
    It is a model for storing all the tasks picked by a Worker.
    """
    status = (
        ('ST', 'Started Task'),
        ('CT', 'Completed Task'),
        ('AB', 'Aborted by Worker'),
        ('RA', 'Rejected due to accuracy'),
    )
    # user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO add validation to current task to check if value is valid
    task_id = models.CharField(max_length=24)
    job_id = models.CharField(max_length=8)
    user_id = models.IntegerField()
    status = models.CharField(max_length=1, choices=status)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskAllocation(models.Model):
    """
    Defines the model to store allocation details for task. This is updated when task is
    allocated to a worker.
    """
    # TODO add validation to ensure task_id is valid and present in the task database
    task_id     = models.CharField(primary_key=True, max_length=24)
    job_id      = models.CharField(max_length=8)
    worker_list = ArrayField(base_field=models.IntegerField(), default=list)

class Request(models.Model):
    """
    Todo:
    """
    email_id   = models.EmailField(primary_key=True)
    created_at = models.DateTimeField()
    secret_key = models.CharField(max_length=128)