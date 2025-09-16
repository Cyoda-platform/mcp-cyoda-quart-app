"""
Pet Registration Processor for Purrfect Pets API.

Handles the registration of new pets in the system.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetRegistrationProcessor(CyodaProcessor):
    """Processor to register a new pet in the system."""

    def __init__(self, name: str = "PetRegistrationProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Register a new pet in the system"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet registration."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(
                    self.name, f"Expected Pet entity, got {type(entity)}"
                )

            pet = entity

            # Validate required fields
            self._validate_required_fields(pet)

            # Verify owner exists (in a real system, this would check the database)
            await self._verify_owner_exists(pet.owner_id)

            # Set registration date if not already set
            if not pet.registration_date:
                pet.registration_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Set initial active status
            pet.is_active = True

            # Generate unique pet_id if not provided
            if not pet.pet_id:
                pet.pet_id = f"PET-{pet.entity_id[:8].upper()}"

            # Log registration event
            pet.add_metadata("registration_processor", self.name)
            pet.add_metadata(
                "registration_timestamp", datetime.now(timezone.utc).isoformat()
            )

            logger.info(
                f"Successfully registered pet {pet.pet_id} for owner {pet.owner_id}"
            )

            return pet

        except Exception as e:
            logger.exception(f"Failed to register pet {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to register pet: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet)

    def _validate_required_fields(self, pet: Pet) -> None:
        """Validate that all required fields are present."""
        if not pet.name or not pet.name.strip():
            raise ValueError("Pet name is required")

        if not pet.species or not pet.species.strip():
            raise ValueError("Pet species is required")

        if not pet.owner_id or not pet.owner_id.strip():
            raise ValueError("Pet owner_id is required")

    async def _verify_owner_exists(self, owner_id: str) -> None:
        """Verify that the owner exists and is active."""
        # In a real implementation, this would query the entity service
        # For now, we'll assume the owner exists if the ID is provided
        if not owner_id:
            raise ValueError("Owner ID is required")

        # TODO: Implement actual owner verification
        # entity_service = self._get_entity_service()
        # owner = await entity_service.get_by_business_id("Owner", owner_id)
        # if not owner or owner.state != "active":
        #     raise ValueError(f"Owner {owner_id} not found or not active")

        logger.debug(f"Owner {owner_id} verification passed (mock)")

    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service

        return get_entity_service()
