"""
EmailDelivery Queue Processor for queuing emails for delivery.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class EmailDeliveryQueueProcessor(CyodaProcessor):
    """Processor to queue emails for delivery."""
    
    def __init__(self, name: str = "EmailDeliveryQueueProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Queues email for delivery"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Queue email for delivery."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(self.name, f"Expected EmailDelivery entity, got {type(entity)}")
            
            # Validate required fields
            if not entity.subscriberId:
                raise ProcessorError(self.name, "EmailDelivery must have subscriberId")
            
            if not entity.catFactId:
                raise ProcessorError(self.name, "EmailDelivery must have catFactId")
            
            # Get entity service to validate subscriber and cat fact
            entity_service = self._get_entity_service()
            
            # Validate subscriber exists and is active
            try:
                subscriber_response = await entity_service.get_by_id(str(entity.subscriberId), "subscriber", "1")
                if not subscriber_response.data.get("isActive"):
                    raise ProcessorError(self.name, "Subscriber is not active")
            except Exception as e:
                raise ProcessorError(self.name, f"Invalid subscriber ID: {entity.subscriberId}")
            
            # Validate cat fact exists
            try:
                await entity_service.get_by_id(str(entity.catFactId), "catfact", "1")
            except Exception as e:
                raise ProcessorError(self.name, f"Invalid cat fact ID: {entity.catFactId}")
            
            # Set queue details
            entity.deliveryAttempts = 0
            entity.lastAttemptDate = datetime.now(timezone.utc)
            
            logger.info(f"Queued email delivery for subscriber {entity.subscriberId}, cat fact {entity.catFactId}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to queue email delivery {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to queue email delivery: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)
    
    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service
        return get_entity_service()
