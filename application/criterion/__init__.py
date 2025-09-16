"""
Application criteria module.
"""

from .active_subscriber_criterion import ActiveSubscriberCriterion
# CatFact criteria
from .catfact_send_time_criterion import CatFactSendTimeCriterion
from .email_validation_criterion import EmailValidationCriterion
from .emaildelivery_bounce_criterion import EmailDeliveryBounceCriterion
from .emaildelivery_failure_criterion import EmailDeliveryFailureCriterion
from .emaildelivery_open_criterion import EmailDeliveryOpenCriterion
from .emaildelivery_retry_criterion import EmailDeliveryRetryCriterion
# EmailDelivery criteria
from .emaildelivery_success_criterion import EmailDeliverySuccessCriterion
# Subscriber criteria
from .subscriber_bounce_criterion import SubscriberBounceCriterion
# WeeklySchedule criteria
from .weeklyschedule_time_criterion import WeeklyScheduleTimeCriterion

__all__ = [
    # Subscriber criteria
    "SubscriberBounceCriterion",
    "EmailValidationCriterion",
    "ActiveSubscriberCriterion",
    # CatFact criteria
    "CatFactSendTimeCriterion",
    # EmailDelivery criteria
    "EmailDeliverySuccessCriterion",
    "EmailDeliveryOpenCriterion",
    "EmailDeliveryFailureCriterion",
    "EmailDeliveryRetryCriterion",
    "EmailDeliveryBounceCriterion",
    # WeeklySchedule criteria
    "WeeklyScheduleTimeCriterion",
]
