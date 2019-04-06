import logging
import os

from django_jinja.builtins import DEFAULT_EXTENSIONS
from kombu import Exchange, Queue

SENDFILE_BACKEND = 'sendfile.backends.development' \
    if DEBUG else 'sendfile.backends.nginx'


def get_variable(field, *args):
    return globals().get(
        field,
        os.environ.get(
            field,
            *args
        )
    )

ALLOWED_HOSTS = get_variable(
    'ALLOWED_HOSTS',
    []
)

if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)

DJANGO_SETTINGS_VERSION = os.environ.get('DJANGO_SETTINGS_VERSION')
DB_NAME = get_variable(
    'DB_NAME',
    'LB_%s' % DJANGO_SETTINGS_VERSION
)
DB_USER = get_variable('DB_USER', DB_NAME)
DB_PASS = get_variable('DB_PASS', DB_NAME)
DB_HOST = get_variable('DB_HOST', '127.0.0.1')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': '5432',
    },
}

GOOGLE_CLOUD_SECRET = get_variable('GOOGLE_CLOUD_SECRET')
GOOGLE_WEB_CREDENTIALS = get_variable('GOOGLE_WEB_CREDENTIALS')

BUSINESS_APNS_CERTIFICATE = get_variable('BUSINESS_APNS_CERTIFICATE')
CUSTOMERS_APNS_CERTIFICATE = get_variable('CUSTOMERS_APNS_CERTIFICATE')

PUSH_NOTIFICATIONS_SETTINGS = {
    'GCM_API_KEY': GOOGLE_CLOUD_SECRET,
    'APNS_CERTIFICATE': CUSTOMERS_APNS_CERTIFICATE,
}

GOCARDLESS = {
    'access_token': get_variable('GOCARDLESS_ACCESS_TOKEN'),
    'environment': get_variable('GOCARDLESS_ENVIRONMENT'),
    'webhook': {
        'secret': get_variable('GOCARDLESS_WEBHOOK_SECRET'),
    },
    'app': {
        'domain': get_variable('GOCARDLESS_APP_DOMAIN'),
        'client_id': get_variable('GOCARDLESS_APP_CLIENT_ID'),
        'client_secret': get_variable('GOCARDLESS_APP_CLIENT_SECRET'),
        'oauth_baseurl': {
            'live': 'https://connect.gocardless.com',
            'sandbox': 'https://connect-sandbox.gocardless.com'
        },
        'webhook': {
            'secret': get_variable('GOCARDLESS_APP_WEBHOOK_SECRET')
        },
        'redirect': {
            'success': 'lunchbreakstore://gocardless/redirect/success',
            'error': 'lunchbreakstore://gocardless/redirect/error'
        }
    }
}

SMS = {
    'text_template': '{pin} is je Lunchbreak authenticatie code, welkom!',
    'domain': get_variable('SMS_DOMAIN'),
    'plivo': {
        'phone': '+32466900406',
        'auth_id': get_variable('PLIVO_AUTH_ID'),
        'auth_token': get_variable('PLIVO_AUTH_TOKEN'),
        'webhook_url': get_variable('PLIVO_WEBHOOK_URL'),
    },
    'twilio': {
        'phone': '+32460200109',
        'account_sid': get_variable('TWILIO_ACCOUNT_SID'),
        'auth_token': get_variable('TWILIO_AUTH_TOKEN'),
        'webhook_url': get_variable('TWILIO_WEBHOOK_URL'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'constants': {
                'GOOGLE_WEB_CREDENTIALS': GOOGLE_WEB_CREDENTIALS,
                'RAVEN_DSN_PUBLIC': get_variable('RAVEN_DSN_PUBLIC', ''),
            },
            'globals': {
                'url_query': 'frontend.templatetags.globals.url_query'
            },
            'extensions': DEFAULT_EXTENSIONS + [
                'sass_processor.jinja2.ext.SassSrc',
                'compressor.contrib.jinja2ext.CompressorExtension',
            ],
            'filters': {
                'absolute_url': 'frontend.templatetags.filters.absolute_url',
                'list_periods': 'frontend.templatetags.filters.list_periods',
                'naturalweekday': 'frontend.templatetags.filters.naturalweekday',
                'json_weekday_periods': 'frontend.templatetags.filters.json_weekday_periods',
                'money': 'frontend.templatetags.filters.money',
                'amount': 'frontend.templatetags.filters.amount',
                'percentage': 'frontend.templatetags.filters.percentage',
                'humanize_date': 'frontend.templatetags.filters.humanize_date',
            },
            'match_extension': None,
            'default_extension': '.html',
            'app_dirname': 'jinja2',
            'undefined': 'Lunchbreak.jinja2.SilencedUndefined' if not DEBUG else 'jinja2.DebugUndefined',
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

# AMQP environment variables are currently unused. The defaults are used for production.
# These defaults are defined in docker-compose.yml.
CELERY_BROKER_URL = 'amqp://{AMQP_USER}:{AMQP_PASSWORD}@{AMQP_HOST}:5672'.format(
    AMQP_USER=get_variable('AMQP_USER', 'lunchbreak'),
    AMQP_PASSWORD=get_variable('AMQP_PASSWORD', 'lunchbreak'),
    AMQP_HOST=get_variable('AMQP_HOST', 'rabbitmq')
)
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_DEFAULT_QUEUE = DJANGO_SETTINGS_VERSION
CELERY_TASK_DEFAULT_EXCHANGE = DJANGO_SETTINGS_VERSION
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'task.default'
CELERY_TASK_QUEUES = (
    Queue(
        CELERY_TASK_DEFAULT_QUEUE,
        exchange=Exchange(
            CELERY_TASK_DEFAULT_EXCHANGE,
            type=CELERY_TASK_DEFAULT_EXCHANGE_TYPE,
        ),
        routing_key='task.#'
    ),
)

# Raven configuration for Sentry
RAVEN_CONFIG = {
    'dsn': get_variable('RAVEN_DSN', None),
    'release': get_variable(
        'VERSION',
        'latest'
    ),
    'environment': DJANGO_SETTINGS_VERSION,
    'CELERY_LOGLEVEL': logging.ERROR,
    'ignore_exceptions': [
        'Http404',
        'django.exceptions.http.Http404',
    ]
}

PAYCONIQ = {
    'webhook_domain': get_variable('PAYCONIQ_WEBHOOK_DOMAIN'),
    'environment': get_variable('PAYCONIQ_ENVIRONMENT', 'testing'),
}
