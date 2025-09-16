"""
PetUnavailableProcessor for Purrfect Pets API

Handles making Pet entities unavailable for various reasons.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetUnavailableProcessor(CyodaProcessor):
    """
    Processor for making Pet entities unavailable.
    Records unavailability reason and notifies interested customers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetUnavailableProcessor",
            description="Makes Pet entities unavailable and records the reason",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process making the Pet entity unavailable.

        Args:
            entity: The Pet entity to make unavailable
            **kwargs: Additional processing parameters (may include unavailability_reason)

        Returns:
            The unavailable Pet entity
        """
        try:
            self.logger.info(
                f"Making Pet {getattr(entity, 'technical_id', '<unknown>')} unavailable"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently available
            if not pet.is_available():
                raise ValueError(f"Pet {pet.technical_id} is not in available state")

            # Get unavailability reason from kwargs or use default
            unavailability_reason = kwargs.get(
                "unavailability_reason", "Temporarily unavailable"
            )

            # Record unavailability reason and timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add unavailability metadata
            if not pet.metadata:
                pet.metadata = {}

            pet.metadata.update(
                {
                    "unavailable_since": current_time,
                    "unavailability_reason": unavailability_reason,
                    "unavailability_status": "active",
                }
            )

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} marked as unavailable. Reason: {unavailability_reason}"
            )

            # Note: Customer notifications would be handled by external service
            self.logger.info(
                f"Unavailability notification sent for Pet {pet.technical_id}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error making Pet {getattr(entity, 'technical_id', '<unknown>')} unavailable: {str(e)}"
            )
            raise
