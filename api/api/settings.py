"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from datetime import timedelta
from .initialize_settings import * 

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_VALUE

# SECURITY WARNING: don't run with debug turned on in production!
if DEBUG_VALUE.lower() == 'true':
    DEBUG = True
else:
    DEBUG = False

#
# Email related configurations
#
EMAIL_BACKEND = EMAIL_BACKEND_VALUE
EMAIL_HOST = EMAIL_HOST_VALUE
EMAIL_PORT = int(EMAIL_PORT_VALUE)
EMAIL_HOST_USER = EMAIL_HOST_USER_VALUE
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD_VALUE
if str(EMAIL_USE_TLS_VALUE).lower() == 'true':
    EMAIL_USE_TLS = True
else:
    EMAIL_USE_TLS = False

ALLOWED_HOSTS = ALLOWED_HOST_VALUE

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'corsheaders',
    'rest_framework',
    'rest_framework_swagger',

    'users',
    'jobs',
   
]

AUTH_USER_MODEL = 'users.User'

if CORS_ORIGIN_ALLOW_ALL_VALUE.lower() == 'true':
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_ALLOW_ALL = False

if not CORS_ORIGIN_ALLOW_ALL:
    CORS_ORIGIN_WHITELIST = CORS_ORIGIN_WHITELIST_VALUE.split(';')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOSTNAME,
        'PORT': DATABASE_PORT,
    }
}

DYNAMO = {
    'URL' : DYNAMO_URL,
    'REGION': DYNAMO_REGION,
}

DYNAMO_AWS_ACCESS = {
     'AWS_ACCESS_KEY_ID' :  AWS_KEY_ID,
     'AWS_SECRET_ACCESS_KEY' : AWS_ACCESS_KEY
}



AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'users.validate.MaximumLengthValidator',
        'OPTIONS': {
            'max_length': 256,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'users.validate.PasswordComplexityValidator',
        'OPTIONS': {
            'min_upper_case_letters': 1,
            'min_lower_case_letters': 1,
            'min_digits'            : 1,
            'min_special_characters': 1,
        }
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CELERY_ENABLE_UTC = False

CELERY_TIMEZONE = 'Asia/Kolkata'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
}

# Add throttling for production environment
if not DEBUG:

    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {'failed_login_attempts' : '10/hr'}



MICRO_SERVICES = {
    'ANNOTATION_ANALYSIS_AND_PROCESSING': RESULT_PROCESSING_URL + '/',
}

SYSTEM_EMAIL_RECIPIENTS = [
    
    'amit.sharma4@w3villa.com',
    
]

CELERY_BROKER_URL = CELERY_BROKER_URL_VALUE
CELERY_ACCEPT_CONTENT = CELERY_ACCEPT_CONTENT_VALUE.split(';')
# Removed temporarily as it is not useful now. Need to implement logging of created celery task
# within application. : Saurabh
# CELERY_RESULT_BACKEND = CELERY_RESULT_BACKEND_VALUE
CELERY_TASK_SERIALIZER = CELERY_TASK_SERIALIZER_VALUE

# parameters defining the age of passwords
PASSWORD_MANAGEMENT_PARAMETERS = {
    'minimum_age' : '1'  ,  # in days
    'maximum_age' : '90'    # in days
}

# time after which an OTP is expired
OTP_EXPIRATION = '24'  # in hours
