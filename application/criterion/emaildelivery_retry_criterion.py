"""
EmailDelivery Retry Criterion for checking if failed email delivery can be retried.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class EmailDeliveryRetryCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if failed email delivery can be retried."""
    
    def __init__(self, name: str = "EmailDeliveryRetryCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if failed email delivery can be retried"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email delivery can be retried."""
        try:
            if not isinstance(entity, EmailDelivery):
                return False
            
            max_retry_attempts = 3
            
            # Check if delivery attempts are below retry limit
            if entity.deliveryAttempts >= max_retry_attempts:
                return False
            
            # Check if failure is not permanent
            if entity.errorMessage:
                if self._is_permanent_failure(entity.errorMessage):
                    return False
            
            # Check minimum retry interval
            if entity.lastAttemptDate:
                try:
                    last_attempt = entity.lastAttemptDate
                    if isinstance(last_attempt, str):
                        last_attempt = datetime.fromisoformat(last_attempt.replace('Z', '+00:00'))
                    
                    time_since_last_attempt = datetime.now(timezone.utc) - last_attempt
                    min_retry_interval = timedelta(hours=1)
                    
                    if time_since_last_attempt >= min_retry_interval:
                        return True
                except (ValueError, AttributeError):
                    # If we can't parse the date, allow retry
                    return True
            
            return False
            
        except Exception as e:
            logger.exception(f"Failed to check retry criteria for email delivery {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check retry criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, EmailDelivery)
    
    def _is_permanent_failure(self, error_message: str) -> bool:
        """Check if failure is permanent."""
        if not error_message:
            return False
        
        permanent_indicators = [
            "permanent", "hard bounce", "invalid email",
            "mailbox does not exist", "domain not found"
        ]
        return any(indicator in error_message.lower() for indicator in permanent_indicators)
