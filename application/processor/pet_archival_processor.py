"""
Pet Archival Processor for Purrfect Pets API.

Handles the permanent archival of pet records.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class PetArchivalProcessor(CyodaProcessor):
    """Processor to permanently archive a pet record."""
    
    def __init__(self, name: str = "PetArchivalProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Permanently archive a pet record"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet archival."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, f"Expected Pet entity, got {type(entity)}")
            
            pet = entity
            
            # Cancel all future appointments
            await self._cancel_all_future_appointments(pet.pet_id)
            
            # Archive medical records (no transition - just update state)
            await self._archive_medical_records(pet.pet_id)
            
            # Set pet as inactive
            pet.is_active = False
            
            # Create archival record
            await self._create_archival_record(pet)
            
            # Notify owner of archival
            await self._notify_owner_of_archival(pet.owner_id, pet.name)
            
            # Log archival event
            pet.add_metadata("archival_processor", self.name)
            pet.add_metadata("archival_timestamp", datetime.now(timezone.utc).isoformat())
            pet.add_metadata("archival_reason", kwargs.get("reason", "Manual archival"))
            pet.add_metadata("archived_by", kwargs.get("archived_by", "system"))
            
            logger.info(f"Successfully archived pet {pet.pet_id}")
            
            return pet
            
        except Exception as e:
            logger.exception(f"Failed to archive pet {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to archive pet: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet)
    
    async def _cancel_all_future_appointments(self, pet_id: str) -> None:
        """Cancel all future appointments for the pet."""
        # Mock implementation - in reality, this would query and update appointments
        logger.info(f"Cancelling all future appointments for pet {pet_id}")
        
        # TODO: Implement actual appointment cancellation
        # entity_service = self._get_entity_service()
        # appointments = await entity_service.search("Appointment", {"pet_id": pet_id})
        # for appointment in appointments:
        #     if appointment.state in ["scheduled", "confirmed"]:
        #         appointment.state = "cancelled"
        #         await entity_service.update(appointment, transition="cancel")
    
    async def _archive_medical_records(self, pet_id: str) -> None:
        """Archive all medical records for the pet."""
        # Mock implementation - transition is null (no state change)
        logger.info(f"Archiving medical records for pet {pet_id}")
        
        # TODO: Implement actual medical record archival
        # entity_service = self._get_entity_service()
        # medical_records = await entity_service.search("MedicalRecord", {"pet_id": pet_id})
        # for record in medical_records:
        #     record.add_metadata("archived_with_pet", True)
        #     await entity_service.update(record)  # No transition
    
    async def _create_archival_record(self, pet: Pet) -> None:
        """Create an archival record for audit purposes."""
        archival_record = {
            "pet_id": pet.pet_id,
            "pet_name": pet.name,
            "owner_id": pet.owner_id,
            "archival_date": datetime.now(timezone.utc).isoformat(),
            "original_registration_date": pet.registration_date,
            "reason": "Pet archival"
        }
        
        logger.info(f"Archival record created: {archival_record}")
        
        # TODO: Store archival record in a dedicated archival system
        # archival_service = self._get_archival_service()
        # await archival_service.create_archival_record(archival_record)
    
    async def _notify_owner_of_archival(self, owner_id: str, pet_name: str) -> None:
        """Notify the owner about pet archival."""
        # Mock implementation - in reality, this would send an email/SMS
        notification_message = f"Your pet {pet_name} has been archived. All records have been preserved for your reference."
        
        logger.info(f"Archival notification sent to owner {owner_id}: {notification_message}")
        
        # TODO: Implement actual notification system
        # notification_service = self._get_notification_service()
        # await notification_service.send_notification(owner_id, notification_message)
    
    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service
        return get_entity_service()
