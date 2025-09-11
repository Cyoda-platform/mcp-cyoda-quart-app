"""
PetReleaseProcessor for Purrfect Pets API

Releases pet reservation and returns to available according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReleaseProcessor(CyodaProcessor):
    """
    Processor for Pet release that releases pet reservation and returns to available inventory.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReleaseProcessor",
            description="Releases pet reservation and returns to available",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity release according to functional requirements.

        Args:
            entity: The Pet entity to release
            **kwargs: Additional processing parameters

        Returns:
            The released pet entity
        """
        try:
            self.logger.info(
                f"Releasing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Remove any existing reservations
            if pet.metadata and "reservation" in pet.metadata:
                old_reservation = pet.metadata["reservation"]
                del pet.metadata["reservation"]
                self.logger.info(f"Removed reservation: {old_reservation}")

            # Clear pending order associations
            if pet.metadata and "order_associations" in pet.metadata:
                old_associations = pet.metadata["order_associations"]
                del pet.metadata["order_associations"]
                self.logger.info(f"Cleared order associations: {old_associations}")

            # Update availability status
            if pet.metadata is None:
                pet.metadata = {}
            pet.metadata["availability_status"] = "available"

            # Log release activity
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            activity_log = {
                "action": "pet_released",
                "timestamp": current_timestamp,
                "details": {
                    "released_by": "PetReleaseProcessor",
                    "reason": kwargs.get("release_reason", "manual_release"),
                },
            }

            if "activity_log" not in pet.metadata:
                pet.metadata["activity_log"] = []
            pet.metadata["activity_log"].append(activity_log)

            # Return pet to available inventory
            pet.metadata["inventory_status"] = "available"

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} released successfully and returned to available inventory"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error releasing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
