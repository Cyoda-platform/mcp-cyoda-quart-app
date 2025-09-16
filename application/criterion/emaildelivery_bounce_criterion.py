"""
EmailDelivery Bounce Criterion for checking if email delivery resulted in a permanent bounce.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class EmailDeliveryBounceCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if email delivery resulted in a permanent bounce."""
    
    def __init__(self, name: str = "EmailDeliveryBounceCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if email delivery resulted in a permanent bounce"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email delivery resulted in permanent bounce."""
        try:
            if not isinstance(entity, EmailDelivery):
                return False
            
            # Check if there's no error message
            if not entity.errorMessage:
                return False
            
            # Check for hard bounce indicators
            hard_bounce_indicators = [
                "hard bounce",
                "permanent failure", 
                "invalid email",
                "mailbox does not exist",
                "domain not found",
                "recipient rejected"
            ]
            
            error_message_lower = entity.errorMessage.lower()
            
            for indicator in hard_bounce_indicators:
                if indicator in error_message_lower:
                    return True
            
            # Check bounce classification with email service provider
            bounce_type = self._check_bounce_classification_with_provider(entity)
            if bounce_type in ["hard", "permanent"]:
                return True
            
            return False
            
        except Exception as e:
            logger.exception(f"Failed to check bounce criteria for email delivery {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check bounce criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, EmailDelivery)
    
    def _check_bounce_classification_with_provider(self, entity: EmailDelivery) -> str:
        """Check bounce classification with email service provider (simulated)."""
        # In real implementation, integrate with actual email service provider
        if entity.errorMessage:
            error_lower = entity.errorMessage.lower()
            if any(indicator in error_lower for indicator in ["hard", "permanent", "invalid"]):
                return "hard"
            else:
                return "soft"
        return "none"
