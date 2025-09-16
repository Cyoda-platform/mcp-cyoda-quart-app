"""
Application criteria module.
"""

# Subscriber criteria
from .subscriber_bounce_criterion import SubscriberBounceCriterion
from .email_validation_criterion import EmailValidationCriterion
from .active_subscriber_criterion import ActiveSubscriberCriterion

# CatFact criteria
from .catfact_send_time_criterion import CatFactSendTimeCriterion

# EmailDelivery criteria
from .emaildelivery_success_criterion import EmailDeliverySuccessCriterion
from .emaildelivery_open_criterion import EmailDeliveryOpenCriterion
from .emaildelivery_failure_criterion import EmailDeliveryFailureCriterion
from .emaildelivery_retry_criterion import EmailDeliveryRetryCriterion
from .emaildelivery_bounce_criterion import EmailDeliveryBounceCriterion

# WeeklySchedule criteria
from .weeklyschedule_time_criterion import WeeklyScheduleTimeCriterion

__all__ = [
    # Subscriber criteria
    'SubscriberBounceCriterion',
    'EmailValidationCriterion',
    'ActiveSubscriberCriterion',
    
    # CatFact criteria
    'CatFactSendTimeCriterion',
    
    # EmailDelivery criteria
    'EmailDeliverySuccessCriterion',
    'EmailDeliveryOpenCriterion',
    'EmailDeliveryFailureCriterion',
    'EmailDeliveryRetryCriterion',
    'EmailDeliveryBounceCriterion',
    
    # WeeklySchedule criteria
    'WeeklyScheduleTimeCriterion'
]
