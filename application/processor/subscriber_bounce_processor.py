"""
Subscriber Bounce Processor for handling permanent email bounces.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class SubscriberBounceProcessor(CyodaProcessor):
    """Processor to handle permanent email bounces."""
    
    def __init__(self, name: str = "SubscriberBounceProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Handles permanent email bounces"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process subscriber bounce."""
        try:
            if not isinstance(entity, Subscriber):
                raise ProcessorError(self.name, f"Expected Subscriber entity, got {type(entity)}")
            
            # Validate subscriber exists
            if not entity.email:
                raise ProcessorError(self.name, "Subscriber email is required")
            
            # Deactivate subscriber due to bounce
            entity.isActive = False
            
            # Add bounce reason to metadata
            bounce_reason = kwargs.get("bounce_reason", "Permanent email bounce")
            entity.add_metadata("bounce_reason", bounce_reason)
            entity.add_metadata("bounced_at", entity.updated_at)
            
            logger.info(f"Bounced subscriber: {entity.email}, reason: {bounce_reason}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to process bounce for subscriber {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to process subscriber bounce: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Subscriber)
