import os


class Base:
    # DEPLOY VARIABLES
    BRANCH = 'master'
    PORT = '8001'

    # DJANGO
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = 'e2a86@j!uc5@z^yu=%n9)6^%w+-(pk8a6@^i!vnvxe^-w%!q8('

    DEBUG = False
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

    DB_PASS = os.environ.get('LB_%s_password' % BRANCH)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'LB_%s' % BRANCH,
            'USER': 'LB_%s' % BRANCH,
            'PASSWORD': DB_PASS,
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
        ],
        'DEFAULT_PARSER_CLASSES': (
            'rest_framework.parsers.JSONParser',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 25
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

    DATETIME_INPUT_FORMATS = (
        '%Y-%m-%d %H:%M',
    )
    TIME_INPUT_FORMATS = (
        '%H:%M',
    )


class Development(Base):
    BRANCH = 'development'

    DEBUG = True
    HOST = '%s.lunchbreakapp.be' % BRANCH

    DB_PASS = os.environ.get('LB_%s_password' % BRANCH)
    DB = 'LB_%s' % BRANCH
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB,
            'USER': DB,
            'PASSWORD': DB_PASS if DB_PASS is not None else DB,
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }


class UWSGI(Development):
    BRANCH = 'uwsgi'


class Travis(Development):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'LB_development',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306'
        }
    }


class Staging(Base):
    BRANCH = 'staging'
    PORT = '8003'

    HOST = '%s.lunchbreakapp.be' % BRANCH
    ALLOWED_HOSTS = [
        HOST
    ]


class Beta(Base):
    BRANCH = 'beta'
    PORT = '8002'

    HOST = '%s.lunchbreakapp.be' % BRANCH
    ALLOWED_HOSTS = [
        HOST
    ]