"""
Pet Reactivation Processor for Purrfect Pets API.

Handles the reactivation of previously deactivated pets.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class PetReactivationProcessor(CyodaProcessor):
    """Processor to reactivate a previously deactivated pet."""
    
    def __init__(self, name: str = "PetReactivationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Reactivate a previously deactivated pet"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet reactivation."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, f"Expected Pet entity, got {type(entity)}")
            
            pet = entity
            
            # Verify owner is still active
            await self._verify_owner_is_still_active(pet.owner_id)
            
            # Set pet as active
            pet.is_active = True
            
            # Notify owner of reactivation
            await self._notify_owner_of_reactivation(pet.owner_id, pet.name)
            
            # Log reactivation event
            pet.add_metadata("reactivation_processor", self.name)
            pet.add_metadata("reactivation_timestamp", datetime.now(timezone.utc).isoformat())
            pet.add_metadata("reactivated_by", kwargs.get("reactivated_by", "system"))
            
            logger.info(f"Successfully reactivated pet {pet.pet_id}")
            
            return pet
            
        except Exception as e:
            logger.exception(f"Failed to reactivate pet {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to reactivate pet: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet)
    
    async def _verify_owner_is_still_active(self, owner_id: str) -> None:
        """Verify that the owner is still active."""
        # In a real implementation, this would query the entity service
        if not owner_id:
            raise ValueError("Owner ID is required")
        
        # TODO: Implement actual owner verification
        # entity_service = self._get_entity_service()
        # owner = await entity_service.get_by_business_id("Owner", owner_id)
        # if not owner or owner.state not in ["active", "verified"]:
        #     raise ValueError(f"Owner {owner_id} not found or not active")
        
        logger.debug(f"Owner {owner_id} active verification passed (mock)")
    
    async def _notify_owner_of_reactivation(self, owner_id: str, pet_name: str) -> None:
        """Notify the owner about pet reactivation."""
        # Mock implementation - in reality, this would send an email/SMS
        notification_message = f"Great news! Your pet {pet_name} has been reactivated and is ready for appointments again."
        
        logger.info(f"Reactivation notification sent to owner {owner_id}: {notification_message}")
        
        # TODO: Implement actual notification system
        # notification_service = self._get_notification_service()
        # await notification_service.send_notification(owner_id, notification_message)
    
    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service
        return get_entity_service()
