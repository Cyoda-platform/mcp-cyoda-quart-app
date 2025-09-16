"""
Subscriber Unsubscribe Processor for handling subscriber unsubscription.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class SubscriberUnsubscribeProcessor(CyodaProcessor):
    """Processor to handle subscriber unsubscription."""
    
    def __init__(self, name: str = "SubscriberUnsubscribeProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Processes subscriber unsubscription"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process subscriber unsubscription."""
        try:
            if not isinstance(entity, Subscriber):
                raise ProcessorError(self.name, f"Expected Subscriber entity, got {type(entity)}")
            
            # Validate subscriber exists and is active
            if not entity.isActive:
                raise ProcessorError(self.name, "Subscriber is already inactive")
            
            # Deactivate subscriber
            entity.isActive = False
            
            logger.info(f"Unsubscribed subscriber: {entity.email}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to unsubscribe subscriber {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to unsubscribe subscriber: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Subscriber)
