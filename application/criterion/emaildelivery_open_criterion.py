"""
EmailDelivery Open Criterion for checking if email was opened by recipient.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class EmailDeliveryOpenCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if email was opened by recipient."""
    
    def __init__(self, name: str = "EmailDeliveryOpenCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if email was opened by recipient"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email was opened."""
        try:
            if not isinstance(entity, EmailDelivery):
                return False
            
            # Check if already marked as opened
            if entity.opened:
                return True
            
            # In a real implementation, check tracking data for email open events
            # For now, simulate open detection
            open_event_detected = self._check_tracking_data_for_open_events(entity)
            return open_event_detected
            
        except Exception as e:
            logger.exception(f"Failed to check open criteria for email delivery {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check open criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, EmailDelivery)
    
    def _check_tracking_data_for_open_events(self, entity: EmailDelivery) -> bool:
        """Check tracking data for email open events (simulated)."""
        # In real implementation, check with email tracking service
        # For now, return False (no open detected)
        return False
