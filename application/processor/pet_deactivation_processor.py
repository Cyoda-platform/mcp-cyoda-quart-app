"""
Pet Deactivation Processor for Purrfect Pets API.

Handles the temporary deactivation of pets.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetDeactivationProcessor(CyodaProcessor):
    """Processor to temporarily deactivate a pet."""

    def __init__(self, name: str = "PetDeactivationProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Temporarily deactivate a pet"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet deactivation."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(
                    self.name, f"Expected Pet entity, got {type(entity)}"
                )

            pet = entity

            # Cancel future appointments
            await self._cancel_future_appointments(pet.pet_id)

            # Set pet as inactive
            pet.is_active = False

            # Notify owner of deactivation
            await self._notify_owner_of_deactivation(pet.owner_id, pet.name)

            # Log deactivation event
            pet.add_metadata("deactivation_processor", self.name)
            pet.add_metadata(
                "deactivation_timestamp", datetime.now(timezone.utc).isoformat()
            )
            pet.add_metadata(
                "deactivation_reason", kwargs.get("reason", "Manual deactivation")
            )

            logger.info(f"Successfully deactivated pet {pet.pet_id}")

            return pet

        except Exception as e:
            logger.exception(f"Failed to deactivate pet {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to deactivate pet: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet)

    async def _cancel_future_appointments(self, pet_id: str) -> None:
        """Cancel all future appointments for the pet."""
        # Mock implementation - in reality, this would query and update appointments
        logger.info(f"Cancelling future appointments for pet {pet_id}")

        # TODO: Implement actual appointment cancellation
        # entity_service = self._get_entity_service()
        # appointments = await entity_service.search("Appointment", {"pet_id": pet_id, "status": "scheduled"})
        # for appointment in appointments:
        #     appointment.state = "cancelled"
        #     await entity_service.update(appointment, transition="cancel")

    async def _notify_owner_of_deactivation(self, owner_id: str, pet_name: str) -> None:
        """Notify the owner about pet deactivation."""
        # Mock implementation - in reality, this would send an email/SMS
        notification_message = f"Your pet {pet_name} has been temporarily deactivated. Please contact us if you have any questions."

        logger.info(
            f"Deactivation notification sent to owner {owner_id}: {notification_message}"
        )

        # TODO: Implement actual notification system
        # notification_service = self._get_notification_service()
        # await notification_service.send_notification(owner_id, notification_message)

    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service

        return get_entity_service()
