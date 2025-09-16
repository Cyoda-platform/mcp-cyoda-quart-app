"""
EmailDelivery Confirmation Processor for confirming email delivery.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class EmailDeliveryConfirmationProcessor(CyodaProcessor):
    """Processor to confirm email delivery."""
    
    def __init__(self, name: str = "EmailDeliveryConfirmationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Confirms email delivery"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Confirm email delivery."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(self.name, f"Expected EmailDelivery entity, got {type(entity)}")
            
            # Validate email was sent
            if not entity.sentDate:
                raise ProcessorError(self.name, "Email must be sent before confirmation")
            
            # Add confirmation metadata
            entity.add_metadata("delivery_confirmed_at", entity.updated_at)
            entity.add_metadata("confirmation_method", "Email service provider confirmation")
            
            logger.info(f"Confirmed email delivery for subscriber {entity.subscriberId}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to confirm email delivery {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to confirm email delivery: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)
