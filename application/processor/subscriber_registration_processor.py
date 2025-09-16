"""
Subscriber Registration Processor for handling new subscriber registrations.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class SubscriberRegistrationProcessor(CyodaProcessor):
    """Processor to handle new subscriber registration."""
    
    def __init__(self, name: str = "SubscriberRegistrationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Processes new subscriber registration"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process new subscriber registration."""
        try:
            if not isinstance(entity, Subscriber):
                raise ProcessorError(self.name, f"Expected Subscriber entity, got {type(entity)}")
            
            # Get entity service
            entity_service = self._get_entity_service()
            
            # Validate email format (already done by Pydantic EmailStr)
            if not entity.email:
                raise ProcessorError(self.name, "Email is required for registration")
            
            # Check if email already exists
            existing_subscribers = await entity_service.find_all("subscriber", "1")
            for existing in existing_subscribers:
                if existing.data.get("email") == entity.email:
                    if existing.data.get("isActive"):
                        raise ProcessorError(self.name, "Email already subscribed and active")
                    else:
                        # Reactivate existing subscriber
                        entity.id = existing.data.get("id")
                        entity.technical_id = existing.technical_id
                        entity.isActive = False  # Will be activated in next step
                        entity.subscriptionDate = datetime.now(timezone.utc)
                        entity.unsubscribeToken = str(uuid.uuid4())
                        return entity
            
            # Set registration details
            entity.subscriptionDate = datetime.now(timezone.utc)
            entity.isActive = False  # Will be activated later
            entity.unsubscribeToken = str(uuid.uuid4())
            
            logger.info(f"Registered new subscriber: {entity.email}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to register subscriber {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to register subscriber: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Subscriber)
    
    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service
        return get_entity_service()
