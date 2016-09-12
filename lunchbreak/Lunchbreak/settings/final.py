import os

ALLOWED_HOSTS = globals().get(
    'ALLOWED_HOSTS',
    os.environ.get(
        'ALLOWED_HOSTS',
        []
    )
)

if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)

DB_NAME = globals().get(
    'DB_NAME',
    os.environ.get(
        'DB_NAME',
        'LB_%s' % BRANCH
    )
)
DB_USER = globals().get(
    'DB_USER',
    os.environ.get(
        'DB_USER',
        DB_NAME
    )
)
DB_PASS = globals().get(
    'DB_PASS',
    os.environ.get(
        'DB_PASS',
        DB_NAME
    )
)
DB_HOST = globals().get(
    'DB_HOST',
    os.environ.get(
        'DB_HOST',
        'localhost'
    )
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': '3306'
    }
}

GOOGLE_CLOUD_SECRET = globals().get(
    'GOOGLE_CLOUD_SECRET',
    os.environ.get(
        'GOOGLE_CLOUD_SECRET'
    )
)

BUSINESS_APNS_CERTIFICATE = globals().get(
    'BUSINESS_APNS_CERTIFICATE',
    os.environ.get(
        'BUSINESS_APNS_CERTIFICATE',
        'certificates/apns/business_development.pem'
    )
)

CUSTOMERS_APNS_CERTIFICATE = globals().get(
    'CUSTOMERS_APNS_CERTIFICATE',
    os.environ.get(
        'CUSTOMERS_APNS_CERTIFICATE',
        'certificates/apns/customers_development.pem'
    )
)

PUSH_NOTIFICATIONS_SETTINGS = {
    'GCM_API_KEY': GOOGLE_CLOUD_SECRET,
    'APNS_CERTIFICATE': CUSTOMERS_APNS_CERTIFICATE,
}


# GoCardless settings
GOCARDLESS = {
    'access_token': globals().get(
        'GOCARDLESS_ACCESS_TOKEN',
        os.environ.get(
            'GOCARDLESS_ACCESS_TOKEN'
        )
    ),
    'environment': 'sandbox',
    'webhook': {
        'secret': globals().get(
            'GOCARDLESS_WEBHOOK_SECRET',
            os.environ.get(
                'GOCARDLESS_WEBHOOK_SECRET'
            )
        ),
    },
    'app': {
        'redirect_uri': globals().get(
            'GOCARDLESS_APP_REDIRECT_URI',
            os.environ.get(
                'GOCARDLESS_APP_REDIRECT_URI'
            )
        ),
        'client_id': globals().get(
            'GOCARDLESS_APP_CLIENT_ID',
            os.environ.get(
                'GOCARDLESS_APP_CLIENT_ID'
            )
        ),
        'client_secret': globals().get(
            'GOCARDLESS_APP_CLIENT_SECRET',
            os.environ.get(
                'GOCARDLESS_APP_CLIENT_SECRET'
            )
        ),
        'oauth_baseurl': {
            'live': 'https://connect.gocardless.com',
            'sandbox': 'https://connect-sandbox.gocardless.com'
        },
        'webhook': {
            'secret': globals().get(
                'GOCARDLESS_APP_WEBHOOK_SECRET',
                os.environ.get(
                    'GOCARDLESS_APP_WEBHOOK_SECRET'
                )
            )
        },
        'redirect': {
            'success': reverse_lazy(
                'frontend-account', kwargs={
                    'status': 'success'
                }
            ),
            'error': reverse_lazy(
                'frontend-account', kwargs={
                    'status': 'error'
                }
            )
        }
    },
    'app_redirect': {
        'success': 'lunchbreakstore://gocardless/redirectflow/success',
        'error': {
            'default': 'lunchbreakstore://gocardless/redirectflow/error',
            'invalid': 'lunchbreakstore://gocardless/redirectflow/error/invalid',
            'incomplete': 'lunchbreakstore://gocardless/redirectflow/error/incomplete',
            'completed': 'lunchbreakstore://gocardless/redirectflow/error/completed',
        }
    }
}
