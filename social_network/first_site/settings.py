from pathlib import Path

import dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv.load_dotenv(BASE_DIR / 'test.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SEND_EMAILS = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # project apps
    'main_app.apps.MainAppConfig',
    'chat_app.apps.ChatAppConfig',

    # another apps
    'crispy_forms',
    'captcha',
    'django_cleanup.apps.CleanupConfig',
    'channels'
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'core.middleware.request_exposer.RequestExposerMiddleware'
]

ROOT_URLCONF = 'first_site.urls'


MAIN_TEMPLATE_DIR = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [MAIN_TEMPLATE_DIR],
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

WSGI_APPLICATION = 'first_site.wsgi.application'
ASGI_APPLICATION = 'first_site.asgi.application'

CHANNEL_REDIS_HOST = os.environ.get('CHANNEL_REDIS_HOST')
CHANNEL_REDIS_PORT = os.environ.get('CHANNEL_REDIS_PORT')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(CHANNEL_REDIS_HOST, CHANNEL_REDIS_PORT)],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('ENGINE'),
        'NAME': os.environ.get('NAME'),
        'HOST': os.environ.get('HOST'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASSWORD')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = ''

AUTH_USER_MODEL = 'main_app.CustomUser'

AUTHENTICATION_BACKENDS = (
    'main_app.backends.CustomBackend',
)

LOGIN_URL = '/main/accounts/login/'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Message broker settings

# Celery with redis
# CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
# CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# Celery with RabbitMQ
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

# Email settings

MY_EMAIL = os.environ.get('MY_EMAIL')
MY_EMAIL_PASSWORD = os.environ.get('MY_EMAIL_PASSWORD')

DEFAULT_FROM_EMAIL = MY_EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_SSL = True

EMAIL_HOST_USER = MY_EMAIL
EMAIL_HOST_PASSWORD = MY_EMAIL_PASSWORD

DEFAULT_EMAIL_LOGIN_SUBJECT = 'Вход в аккаунт'
DEFAULT_EMAIL_LOGIN_BODY = 'Здравствуйте, {name}\n\nВ ваш аккаунт на сайте ИНСТАМЕТР был выполнен вход\n\n' \
                           'Ваше имя пользователя: {username}\n' \
                           '\nЕсли это были не вы, измените пароль\n\n{date}'

DEFAULT_EMAIL_SETTINGS_CHANGED_SUBJECT = 'Кто-то пытался изменить настройки вашего аккаунта'
DEFAULT_EMAIL_SETTINGS_CHANGED_BODY = 'Здравствуйте, {name}\n\nКто-то пытался изменить или изменил настройки вашего ' \
                                      'аккаунта\n\nЕсли это были не вы, измените пароль.\n\n{date}'

DEFAULT_EMAIL_FRIEND_REQUEST_SUBJECT = 'Новая заявка в друзья'
DEFAULT_EMAIL_FRIEND_REQUEST_BODY = 'Здравствуйте, {name}\n\n{name_requested} отправил вам заявку в друзья\n\n{date}'


# Cache setting

# CACHES = {
#     'default':
#         {
#             'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#             'LOCATION': 'redis://127.0.0.1:6379'
#         }
# }

if DEBUG:
    # Applying debug toolbar
    import mimetypes

    INTERNAL_IPS = [
        '127.0.0.1'
    ]

    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

    INSTALLED_APPS += [
        'debug_toolbar'
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware'
    ]
