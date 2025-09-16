"""
Pet Activation Processor for Purrfect Pets API.

Handles the activation of registered pets for appointments and services.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class PetActivationProcessor(CyodaProcessor):
    """Processor to activate a registered pet for appointments and services."""
    
    def __init__(self, name: str = "PetActivationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Activate a registered pet for appointments and services"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet activation."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, f"Expected Pet entity, got {type(entity)}")
            
            pet = entity
            
            # Verify owner is still active
            await self._verify_owner_is_active(pet.owner_id)
            
            # Set pet as active
            pet.is_active = True
            
            # Create welcome notification (mock implementation)
            await self._create_welcome_notification(pet.owner_id, pet.name)
            
            # Log activation event
            pet.add_metadata("activation_processor", self.name)
            pet.add_metadata("activation_timestamp", datetime.now(timezone.utc).isoformat())
            pet.add_metadata("activated_by", "system")
            
            logger.info(f"Successfully activated pet {pet.pet_id} for owner {pet.owner_id}")
            
            return pet
            
        except Exception as e:
            logger.exception(f"Failed to activate pet {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to activate pet: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet)
    
    async def _verify_owner_is_active(self, owner_id: str) -> None:
        """Verify that the owner is still active."""
        # In a real implementation, this would query the entity service
        # For now, we'll assume the owner is active if the ID is provided
        if not owner_id:
            raise ValueError("Owner ID is required")
        
        # TODO: Implement actual owner verification
        # entity_service = self._get_entity_service()
        # owner = await entity_service.get_by_business_id("Owner", owner_id)
        # if not owner or owner.state != "active":
        #     raise ValueError(f"Owner {owner_id} not found or not active")
        
        logger.debug(f"Owner {owner_id} active verification passed (mock)")
    
    async def _create_welcome_notification(self, owner_id: str, pet_name: str) -> None:
        """Create a welcome notification for the owner."""
        # Mock implementation - in reality, this would send an email/SMS
        notification_message = f"Welcome! Your pet {pet_name} has been successfully activated and is ready for appointments."
        
        logger.info(f"Welcome notification created for owner {owner_id}: {notification_message}")
        
        # TODO: Implement actual notification system
        # notification_service = self._get_notification_service()
        # await notification_service.send_notification(owner_id, notification_message)
    
    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service
        return get_entity_service()
