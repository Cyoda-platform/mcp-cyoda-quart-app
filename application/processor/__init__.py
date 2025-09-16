"""
Application processors module.
"""

# Subscriber processors
from .subscriber_registration_processor import SubscriberRegistrationProcessor
from .subscriber_activation_processor import SubscriberActivationProcessor
from .subscriber_unsubscribe_processor import SubscriberUnsubscribeProcessor
from .subscriber_bounce_processor import SubscriberBounceProcessor
from .subscriber_reactivation_processor import SubscriberReactivationProcessor

# CatFact processors
from .catfact_retrieval_processor import CatFactRetrievalProcessor
from .catfact_scheduling_processor import CatFactSchedulingProcessor
from .catfact_distribution_processor import CatFactDistributionProcessor
from .catfact_archive_processor import CatFactArchiveProcessor

# EmailDelivery processors
from .emaildelivery_queue_processor import EmailDeliveryQueueProcessor
from .emaildelivery_send_processor import EmailDeliverySendProcessor
from .emaildelivery_confirmation_processor import EmailDeliveryConfirmationProcessor
from .emaildelivery_open_processor import EmailDeliveryOpenProcessor
from .emaildelivery_failure_processor import EmailDeliveryFailureProcessor
from .emaildelivery_retry_processor import EmailDeliveryRetryProcessor
from .emaildelivery_bounce_processor import EmailDeliveryBounceProcessor

# WeeklySchedule processors
from .weeklyschedule_creation_processor import WeeklyScheduleCreationProcessor
from .weeklyschedule_fact_retrieval_processor import WeeklyScheduleFactRetrievalProcessor
from .weeklyschedule_email_distribution_processor import WeeklyScheduleEmailDistributionProcessor
from .weeklyschedule_completion_processor import WeeklyScheduleCompletionProcessor

__all__ = [
    # Subscriber processors
    'SubscriberRegistrationProcessor',
    'SubscriberActivationProcessor', 
    'SubscriberUnsubscribeProcessor',
    'SubscriberBounceProcessor',
    'SubscriberReactivationProcessor',
    
    # CatFact processors
    'CatFactRetrievalProcessor',
    'CatFactSchedulingProcessor',
    'CatFactDistributionProcessor',
    'CatFactArchiveProcessor',
    
    # EmailDelivery processors
    'EmailDeliveryQueueProcessor',
    'EmailDeliverySendProcessor',
    'EmailDeliveryConfirmationProcessor',
    'EmailDeliveryOpenProcessor',
    'EmailDeliveryFailureProcessor',
    'EmailDeliveryRetryProcessor',
    'EmailDeliveryBounceProcessor',
    
    # WeeklySchedule processors
    'WeeklyScheduleCreationProcessor',
    'WeeklyScheduleFactRetrievalProcessor',
    'WeeklyScheduleEmailDistributionProcessor',
    'WeeklyScheduleCompletionProcessor'
]
