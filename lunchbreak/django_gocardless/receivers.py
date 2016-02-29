from .models import Mandate, Payment, Payout, Refund, Subscription
from .signals import *

mandate_created.connect(
    Mandate.created,
    dispatch_uid='dgc_mandate_created'
)
mandate_submitted.connect(
    Mandate.submitted,
    dispatch_uid='dgc_mandate_submitted'
)
mandate_active.connect(
    Mandate.active,
    dispatch_uid='dgc_mandate_active'
)
mandate_reinstated.connect(
    Mandate.reinstated,
    dispatch_uid='dgc_mandate_reinstated'
)
mandate_transferred.connect(
    Mandate.transferred,
    dispatch_uid='dgc_mandate_transferred'
)
mandate_cancelled.connect(
    Mandate.cancelled,
    dispatch_uid='dgc_mandate_cancelled'
)
mandate_failed.connect(
    Mandate.failed,
    dispatch_uid='dgc_mandate_failed'
)
mandate_expired.connect(
    Mandate.expired,
    dispatch_uid='dgc_mandate_expired'
)
mandate_resubmission_requested.connect(
    Mandate.resubmission_requested,
    dispatch_uid='dgc_mandate_resubmission_requested'
)

payment_created.connect(
    Payment.created,
    dispatch_uid='dgc_payment_created'
)
payment_submitted.connect(
    Payment.submitted,
    dispatch_uid='dgc_payment_submitted'
)
payment_confirmed.connect(
    Payment.confirmed,
    dispatch_uid='dgc_payment_confirmed'
)
payment_cancelled.connect(
    Payment.cancelled,
    dispatch_uid='dgc_payment_cancelled'
)
payment_failed.connect(
    Payment.failed,
    dispatch_uid='dgc_payment_failed'
)
payment_charged_back.connect(
    Payment.charged_back,
    dispatch_uid='dgc_payment_charged_back'
)
payment_chargeback_cancelled.connect(
    Payment.chargeback_cancelled,
    dispatch_uid='dgc_payment_chargeback_cancelled'
)
payment_paid_out.connect(
    Payment.paid_out,
    dispatch_uid='dgc_payment_paid_out'
)
payment_late_failure_settled.connect(
    Payment.late_failure_settled,
    dispatch_uid='dgc_payment_late_failure_settled'
)
payment_chargeback_settled.connect(
    Payment.chargeback_settled,
    dispatch_uid='dgc_payment_chargeback_settled'
)
payment_resubmission_requested.connect(
    Payment.resubmission_requested,
    dispatch_uid='dgc_payment_resubmission_requested'
)

subscription_created.connect(
    Subscription.created,
    dispatch_uid='dgc_subscription_created'
)
subscription_payment_created.connect(
    Subscription.created,
    dispatch_uid='dgc_subscription_payment_created'
)
subscription_cancelled.connect(
    Subscription.created,
    dispatch_uid='dgc_subscription_cancelled'
)

payout_paid.connect(
    Payout.paid,
    dispatch_uid='dgc_payout_paid'
)

refund_created.connect(
    Refund.created,
    dispatch_uid='dgc_refund_created'
)
refund_paid.connect(
    Refund.paid,
    dispatch_uid='dgc_refund_paid'
)
refund_settled.connect(
    Refund.settled,
    dispatch_uid='dgc_refund_settled'
)
