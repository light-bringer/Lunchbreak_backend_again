from Lunchbreak.exceptions import LunchbreakException
from rest_framework import status

COSTCHECK_FAILED = 700
PREORDERTIME_EXCEEDED = 701
PASTORDER_DENIED = 702
STORE_CLOSED = 704
# 705
MINDAYS_EXCEEDED = 706
USER_DISABLED = 707
# 708
# 709
# 710
# 711
GOCARDLESS_DISABLED = 712
NO_PAYMENT_LINK = 713
PAYMENT_LINK_NOT_CONFIRMED = 714
ORDEREDFOOD_NOT_ORIGINAL = 715
ONLINE_PAYMENT_REQUIRED = 716
CASH_DISABLED = 717


class PastOrderDenied(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PASTORDER_DENIED
    default_detail = 'Een bestelling moet in de toekomst geplaatst worden.'


class CostCheckFailed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = COSTCHECK_FAILED
    default_detail = 'Prijs komt niet overeen met berekende prijs.'


class PreorderTimeExceeded(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PREORDERTIME_EXCEEDED
    default_detail = 'Een bestelling moet langer op voorhand geplaatst worden.'


class StoreClosed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = STORE_CLOSED
    default_detail = 'De winkel is gesloten op het gegeven moment.'


class MinDaysExceeded(PreorderTimeExceeded):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = MINDAYS_EXCEEDED
    # information see PreorderTimeExceeded


class UserDisabled(LunchbreakException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = USER_DISABLED
    default_detail = 'Deze account werd uitgeschakeld.'


class GoCardlessDisabled(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = GOCARDLESS_DISABLED
    default_detail = 'Deze winkel heeft GoCardless uitgeschakeld.'


class NoPaymentLink(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = NO_PAYMENT_LINK
    default_detail = 'Gebruiker heeft geen mandaat met deze winkel getekend.'


class PaymentLinkNotConfirmed(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = PAYMENT_LINK_NOT_CONFIRMED
    default_detail = 'Gebruiker heeft het mandaat nog niet bevestigd.'


class OrderedFoodNotOriginal(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ORDEREDFOOD_NOT_ORIGINAL
    default_detail = 'Het originele waar moet gelijk zijn aan het meest aansluitende waar.'


class OnlinePaymentRequired(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ONLINE_PAYMENT_REQUIRED
    default_detail = 'Online betalen is verplicht bij deze bestelling.'


class CashDisabled(LunchbreakException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = CASH_DISABLED
    default_detail = 'Deze winkel heeft cash betalingen uitgeschakeld.'
