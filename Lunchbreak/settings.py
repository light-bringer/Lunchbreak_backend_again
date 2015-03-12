import os

from configurations import Configuration


class Base(Configuration):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = 'e2a86@j!uc5@z^yu=%n9)6^%w+-(pk8a6@^i!vnvxe^-w%!q8('

    DEBUG = True
    TEMPLATE_DEBUG = True
    HOST = 'api.lunchbreakapp.be'
    ALLOWED_HOSTS = [
        HOST
    ]

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'rest_framework',
        'opbeat.contrib.django',

        'business',
        'customers',
        'lunch',
    )

    MIDDLEWARE_CLASSES = (
        'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    ROOT_URLCONF = 'Lunchbreak.urls'

    WSGI_APPLICATION = 'Lunchbreak.wsgi.application'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'lunchbreak_development',
            'USER': 'lunchbreak',
            'PASSWORD': 'lunchbreak',
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    )

    LANGUAGE_CODE = 'nl-be'
    TIME_ZONE = 'Europe/Brussels'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    STATIC_ROOT = BASE_DIR + '/static/'
    STATIC_URL = '/static/'
    TEMPLATE_DIRS = (
        BASE_DIR + '/business/templates/',
    )

    APPEND_SLASH = True

    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'lunch.exceptions.lunchbreakExceptionHandler',
        'COERCE_DECIMAL_TO_STRING': False,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ]
    }

    OPBEAT = {
        'ORGANIZATION_ID': '308fe549a8c042429061395a87bb662a',
        'APP_ID': 'a475a69ed8',
        'SECRET_TOKEN': 'e2e3be25fe41c9323f8f4384549d7c22f8c2422e',
        'DEBUG': False
    }

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['opbeat'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
            },
        },
        'handlers': {
            'opbeat': {
                'level': 'ERROR',
                'class': 'opbeat.contrib.django.handlers.OpbeatHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'opbeat': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'opbeat.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'M8cDQH8m3WLstEfLuKphqCalsy5eSJyW5xtQIQLd8viPPM9tfyQimqCMiBxF7CN9owMp80STdM7cdepLcPCQhIPmNJeOhE4yTr2pIcUa1mmreywzcRactiNQVAo1gy9b'
    EMAIL_HOST_PASSWORD = 'JmxxhBcM45A4Phth3SzMa0Lqfyd2qRgvT7a4aGnrHz8yTROmQL'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_FROM = 'noreply@lunchbreakapp.be'


class Development(Base):
    DEBUG = True
    HOST = 'localhost:8000'


class Travis(Development):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'lunchbreak_development',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }
