"""
CatFact Distribution Processor for distributing cat facts to all active subscribers.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.catfact.version_1.catfact import CatFact
from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class CatFactDistributionProcessor(CyodaProcessor):
    """Processor to distribute cat facts to all active subscribers."""
    
    def __init__(self, name: str = "CatFactDistributionProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Distributes cat fact to all active subscribers"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Distribute cat fact to all active subscribers."""
        try:
            if not isinstance(entity, CatFact):
                raise ProcessorError(self.name, f"Expected CatFact entity, got {type(entity)}")
            
            # Validate cat fact is scheduled and ready to send
            if not entity.scheduledSendDate:
                raise ProcessorError(self.name, "CatFact must be scheduled before distribution")
            
            if not entity.fact:
                raise ProcessorError(self.name, "CatFact must have content for distribution")
            
            # Get entity service
            entity_service = self._get_entity_service()
            
            # Get all active subscribers
            subscribers = await entity_service.find_all("subscriber", "1")
            active_subscribers = [
                sub for sub in subscribers 
                if sub.data.get("isActive") and sub.data.get("state") == "active"
            ]
            
            distribution_count = 0
            
            # Create EmailDelivery entities for each active subscriber
            for subscriber in active_subscribers:
                try:
                    email_delivery_data = {
                        "subscriberId": subscriber.data.get("id"),
                        "catFactId": entity.id,
                        "deliveryAttempts": 0
                    }
                    
                    # Save EmailDelivery entity (this will trigger its workflow)
                    await entity_service.save(email_delivery_data, "emaildelivery", "1")
                    distribution_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to create email delivery for subscriber {subscriber.data.get('id')}: {e}")
                    continue
            
            # Add distribution metadata
            entity.add_metadata("distribution_count", distribution_count)
            entity.add_metadata("distributed_at", entity.updated_at)
            
            logger.info(f"Distributed cat fact to {distribution_count} subscribers")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to distribute cat fact {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to distribute cat fact: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, CatFact)
    
    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service
        return get_entity_service()
