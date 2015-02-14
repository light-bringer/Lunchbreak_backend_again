from rest_framework import status

from lunch.exceptions import LunchbreakException

from opbeat.contrib.django.models import logger


AUTHENTICATION_FAILED = 700
COSTCHECK_FAILED = 701
MINTIME_EXCEEDED = 702
PASTORDER_DENIED = 703
DIGITS_UNAVAILABLE = 704

DIGITS_LEGACY_ERROR = 0
DIGITS_INVALID_PHONE = 32
DIGITS_APP_AUTH_ERROR = 89
DIGITS_GUEST_AUTH_ERROR = 239
DIGITS_PIN_INCORRECT = 236
DIGITS_ALREADY_REGISTERED_ERROR = 285

DIGITS_EXCEPTIONS = {
	DIGITS_LEGACY_ERROR: 'Digits legacy error.',
	DIGITS_INVALID_PHONE: ['Digits invalid phone number.', status.HTTP_400_BAD_REQUEST],
	DIGITS_APP_AUTH_ERROR: 'Digits app authorization failed.',
	DIGITS_GUEST_AUTH_ERROR: 'Digits guest authorization failed.',
	DIGITS_PIN_INCORRECT: ['Incorrect pin.', status.HTTP_400_BAD_REQUEST],
	DIGITS_ALREADY_REGISTERED_ERROR: 'User already in the Digits database.'
}


class DigitsException(LunchbreakException):
	status_code = status.HTTP_503_SERVICE_UNAVAILABLE
	code = DIGITS_UNAVAILABLE
	information = 'Messaging service temporarily unavailable.'

	def __init__(self, code, content):
		detail = None
		if code in DIGITS_EXCEPTIONS:
			info = DIGITS_EXCEPTIONS[code]
			if type(info) is list:
				detail = info[0]
				self.status_code = info[1]
			else:
				detail = info
		else:
			logger.exception('Undocumented Digits exception: %s' % content)
		self.code = code
		super(DigitsException, self).__init__(detail)


class AuthenticationFailed(LunchbreakException):
	status_code = status.HTTP_401_UNAUTHORIZED
	code = AUTHENTICATION_FAILED
	information = 'User authentication failed.'


class CostCheckFailed(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = COSTCHECK_FAILED
	information = 'Cost check failed.'


class MinTimeExceeded(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = MINTIME_EXCEEDED
	information = 'An order must be placed later.'


class PastOrderDenied(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = PASTORDER_DENIED
	information = 'An order must be placed in the future.'

