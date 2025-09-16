"""
EmailDelivery Success Criterion for checking if email delivery was successful.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class EmailDeliverySuccessCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if email delivery was successful."""
    
    def __init__(self, name: str = "EmailDeliverySuccessCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if email delivery was successful"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email delivery was successful."""
        try:
            if not isinstance(entity, EmailDelivery):
                return False
            
            # Check if email was sent
            if not entity.sentDate:
                return False
            
            # Check if there's an error message
            if entity.errorMessage:
                return False
            
            # In a real implementation, check delivery status with email service provider
            # For now, assume success if sent without error
            delivery_status = self._check_delivery_status_with_provider(entity)
            return delivery_status == "delivered"
            
        except Exception as e:
            logger.exception(f"Failed to check success criteria for email delivery {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check success criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, EmailDelivery)
    
    def _check_delivery_status_with_provider(self, entity: EmailDelivery) -> str:
        """Check delivery status with email service provider (simulated)."""
        # In real implementation, integrate with actual email service provider
        # For now, simulate successful delivery if sent without error
        if entity.sentDate and not entity.errorMessage:
            return "delivered"
        return "failed"
