"""Pet Reservation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetReservationProcessor(CyodaProcessor):
    """Processor for reserving pets for specific owners."""

    def __init__(self):
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves pet for specific owner, sets reservation timestamp",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet reservation."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, "Entity must be a Pet instance")

            # Get owner ID from kwargs or entity
            owner_id = kwargs.get("ownerId") or kwargs.get("owner_id")
            if not owner_id and hasattr(entity, "ownerId"):
                owner_id = entity.ownerId

            if not owner_id:
                raise ProcessorError(self.name, "Owner ID is required for reservation")

            # Validate pet is available
            if entity.state not in ["available"]:
                raise ProcessorError(
                    self.name,
                    f"Pet must be available for reservation, current state: {entity.state}",
                )

            # TODO: In a real implementation, validate that owner exists and is ACTIVE
            # This would require EntityService integration

            # Set owner ID and update timestamps
            entity.ownerId = owner_id
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add reservation metadata
            entity.add_metadata("reserved_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("reserved_by", owner_id)
            entity.add_metadata("reservation_processed", True)

            logger.info(f"Successfully reserved pet {entity.name} for owner {owner_id}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process pet reservation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process pet reservation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Pet"
        )
