"""
Subscriber Bounce Criterion for checking if subscriber should be marked as bounced.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class SubscriberBounceCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if subscriber should be marked as bounced."""
    
    def __init__(self, name: str = "SubscriberBounceCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if subscriber should be marked as bounced based on email delivery failures"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if subscriber should be bounced."""
        try:
            if not isinstance(entity, Subscriber):
                return False
            
            # Get entity service to check email delivery records
            entity_service = self._get_entity_service()
            
            # Get recent EmailDelivery records for subscriber
            email_deliveries = await entity_service.find_all("emaildelivery", "1")
            subscriber_deliveries = [
                delivery for delivery in email_deliveries 
                if delivery.data.get("subscriberId") == entity.id
            ]
            
            # Count permanent bounce failures in last 30 days
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            permanent_bounce_count = 0
            
            for delivery in subscriber_deliveries:
                last_attempt = delivery.data.get("lastAttemptDate")
                error_message = delivery.data.get("errorMessage", "")
                
                if last_attempt:
                    try:
                        attempt_date = datetime.fromisoformat(last_attempt.replace('Z', '+00:00'))
                        if attempt_date >= thirty_days_ago:
                            if self._is_permanent_bounce(error_message):
                                permanent_bounce_count += 1
                    except (ValueError, AttributeError):
                        continue
            
            # Check if permanent bounce count exceeds threshold
            if permanent_bounce_count >= 3:
                return True
            
            # Check latest delivery for hard bounce
            if subscriber_deliveries:
                latest_delivery = max(
                    subscriber_deliveries,
                    key=lambda d: d.data.get("lastAttemptDate", ""),
                    default=None
                )
                if latest_delivery:
                    error_message = latest_delivery.data.get("errorMessage", "")
                    if self._is_hard_bounce(error_message):
                        return True
            
            return False
            
        except Exception as e:
            logger.exception(f"Failed to check bounce criteria for subscriber {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check bounce criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Subscriber)
    
    def _is_permanent_bounce(self, error_message: str) -> bool:
        """Check if error indicates permanent bounce."""
        if not error_message:
            return False
        
        permanent_indicators = [
            "permanent failure", "hard bounce", "invalid email",
            "mailbox does not exist", "domain not found"
        ]
        return any(indicator in error_message.lower() for indicator in permanent_indicators)
    
    def _is_hard_bounce(self, error_message: str) -> bool:
        """Check if error indicates hard bounce."""
        if not error_message:
            return False
        
        hard_bounce_indicators = [
            "hard bounce", "permanent failure", "invalid email",
            "mailbox does not exist", "domain not found", "recipient rejected"
        ]
        return any(indicator in error_message.lower() for indicator in hard_bounce_indicators)
    
    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service
        return get_entity_service()
