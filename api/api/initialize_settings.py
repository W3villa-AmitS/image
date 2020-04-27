import os

try:
    SECRET_KEY_FILE = os.environ['SECRET_KEY_FILE']
    with open(SECRET_KEY_FILE, 'r') as f:
        SECRET_KEY_VALUE = f.read()[:-1]

    if os.environ['IF_ENVIRONMENT'].lower() == 'production':
        DEBUG_VALUE = 'false'
    else:
        DEBUG_VALUE = os.environ['DEBUG_VALUE']
    EMAIL_BACKEND_VALUE = os.environ['EMAIL_BACKEND_VALUE']
    EMAIL_HOST_VALUE = os.environ['EMAIL_HOST_VALUE']
    # Value of EMAIL_PORT_VALUE should be converted to int
    EMAIL_PORT_VALUE = os.environ['EMAIL_PORT_VALUE']

    EMAIL_HOST_USER_FILE = os.environ['EMAIL_HOST_USER_FILE']
    with open(EMAIL_HOST_USER_FILE, 'r') as f:
        EMAIL_HOST_USER_VALUE = f.read()[:-1]
    EMAIL_HOST_PASSWORD_FILE = os.environ['EMAIL_HOST_PASSWORD_FILE']
    with open(EMAIL_HOST_PASSWORD_FILE, 'r') as f:
        EMAIL_HOST_PASSWORD_VALUE = f.read()[:-1]

    # Value of EMAIL_USE_TLS_VALUE should be converted to boolean
    EMAIL_USE_TLS_VALUE = os.environ['EMAIL_USE_TLS_VALUE']
    ALLOWED_HOST_VALUE = [os.environ['ALLOWED_HOST_VALUE']]
    # Database setting
    DATABASE_NAME = os.environ['DATABASE_NAME']

    DATABASE_USER_FILE = os.environ['DATABASE_USER_FILE']
    with open(DATABASE_USER_FILE, 'r') as f:
        DATABASE_USER = f.read()[:-1]
    DATABASE_PASSWORD_FILE = os.environ['DATABASE_PASSWORD_FILE']
    with open(DATABASE_PASSWORD_FILE, 'r') as f:
        DATABASE_PASSWORD = f.read()[:-1]

    DATABASE_HOSTNAME = os.environ['DATABASE_HOSTNAME']
    DATABASE_PORT = os.environ['DATABASE_PORT']
    DYNAMO_URL = os.environ['DYNAMO_URL']
    DYNAMO_REGION = os.environ['DYNAMO_REGION']
    RESULT_PROCESSING_URL = os.environ['RESULT_PROCESSING_URL']

    # if False, maintain a CORS whitelist for allowed hosts in production environment
    # Value of CORS_ORIGIN_ALLOW_ALL_VALUE should be converted to boolean
    if os.environ['IF_ENVIRONMENT'].lower() == 'production':
        CORS_ORIGIN_ALLOW_ALL_VALUE = 'false'
        CORS_ORIGIN_WHITELIST_VALUE = os.environ.get['CORS_ORIGIN_WHITELIST_VALUE']
    else:
        CORS_ORIGIN_ALLOW_ALL_VALUE = os.environ['CORS_ORIGIN_ALLOW_ALL_VALUE']
        # environment variable CORS_ORIGIN_WHITELIST_VALUE must contain a semicolon(;) separated list of hosts
        if CORS_ORIGIN_ALLOW_ALL_VALUE.lower()  == 'false':
            CORS_ORIGIN_WHITELIST_VALUE = os.environ.get['CORS_ORIGIN_WHITELIST_VALUE']

    CELERY_BROKER_URL_FILE = os.environ['CELERY_BROKER_URL_FILE']
    with open(CELERY_BROKER_URL_FILE, 'r') as f:
        CELERY_BROKER_URL_VALUE = f.read()[:-1]

    CELERY_ACCEPT_CONTENT_VALUE = os.environ['CELERY_ACCEPT_CONTENT_VALUE']

    CELERY_RESULT_BACKEND_FILE = os.environ['CELERY_RESULT_BACKEND_FILE']
    with open(CELERY_RESULT_BACKEND_FILE, 'r') as f:
        CELERY_RESULT_BACKEND_VALUE = f.read()[:-1]

    CELERY_TASK_SERIALIZER_VALUE = os.environ['CELERY_TASK_SERIALIZER_VALUE']

    AWS_KEY_ID_FILE = os.environ['AWS_KEY_ID_FILE']
    with open(AWS_KEY_ID_FILE, 'r') as f:
        AWS_KEY_ID = f.read()[:-1]

    AWS_ACCESS_KEY_FILE = os.environ['AWS_ACCESS_KEY_FILE']
    with open(AWS_ACCESS_KEY_FILE, 'r') as f:
        AWS_ACCESS_KEY = f.read()[:-1]
except FileNotFoundError:
    raise
except KeyError:
    SECRET_KEY_VALUE = '77sr2bp#&$l+e96p3-e4gwjokqrno$bzuj0yh#y952*lvro^yy'
    DEBUG_VALUE = 'true'
    EMAIL_BACKEND_VALUE = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST_VALUE = 'smtp.gmail.com'
    # Value of EMAIL_PORT_VALUE should be converted to int
    EMAIL_PORT_VALUE = '587'
    EMAIL_HOST_USER_VALUE = 'imagefactory0@gmail.com'
    EMAIL_HOST_PASSWORD_VALUE = 'P}7zxe@F;V(`5)<LUH{:&=f9v.,6MA/DB#4G*tqShZn_m[?dCX'
    # Value of EMAIL_USE_TLS_VALUE should be converted to boolean
    EMAIL_USE_TLS_VALUE = 'True'
    ALLOWED_HOST_VALUE = []
    # Database setting
    DATABASE_NAME = 'image-factory'
    DATABASE_USER = 'postgres-admin'
    DATABASE_PASSWORD = 'password123'
    DATABASE_HOSTNAME = 'localhost'
    DATABASE_PORT = '5432'
    DYNAMO_URL = 'http://localhost:8080'
    DYNAMO_REGION = 'ap-south-1'
    RESULT_PROCESSING_URL = 'http://localhost:5051'
    AWS_KEY_ID = 'Name'
    AWS_ACCESS_KEY = 'key'
    # Check to ensure it is not production environment
    try:
        env = 'development'
        env =  os.environ['IF_ENVIRONMENT'].lower()
        raise
    except:
        if env == 'production' or env == 'staging':
            raise

    # disable CORS whitelist for production environment
    CORS_ORIGIN_ALLOW_ALL_VALUE = 'true'

    CELERY_BROKER_URL_VALUE = 'amqp://guest:guest@0.0.0.0:5673//'
    CELERY_ACCEPT_CONTENT_VALUE = 'json'
    CELERY_RESULT_BACKEND_VALUE = 'dq+sqlite://:results.sqlite'
    CELERY_TASK_SERIALIZER_VALUE = 'json'
