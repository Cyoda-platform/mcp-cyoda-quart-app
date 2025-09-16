"""Pet Reservation Cancel Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetReservationCancelProcessor(CyodaProcessor):
    """Processor for cancelling pet reservations."""

    def __init__(self):
        super().__init__(
            name="PetReservationCancelProcessor",
            description="Cancels pet reservation, makes pet available again",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet reservation cancellation."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, "Entity must be a Pet instance")

            # Validate pet is pending or reserved
            if entity.state not in ["pending", "reserved"]:
                raise ProcessorError(
                    self.name,
                    f"Pet must be pending or reserved for cancellation, current state: {entity.state}",
                )

            # Store previous owner for logging
            previous_owner = entity.ownerId

            # Clear owner reference
            entity.ownerId = None
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add cancellation metadata
            entity.add_metadata(
                "reservation_cancelled_at", datetime.now(timezone.utc).isoformat()
            )
            entity.add_metadata("previous_owner", previous_owner)
            entity.add_metadata("cancellation_processed", True)

            # Remove reservation metadata
            if entity.metadata:
                entity.metadata.pop("reserved_at", None)
                entity.metadata.pop("reserved_by", None)

            logger.info(
                f"Successfully cancelled reservation for pet {entity.name}, previous owner: {previous_owner}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process pet reservation cancellation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name,
                f"Failed to process pet reservation cancellation: {str(e)}",
                e,
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Pet"
        )
