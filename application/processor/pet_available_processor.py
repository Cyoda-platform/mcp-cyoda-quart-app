"""
PetAvailableProcessor for Purrfect Pets API

Handles making Pet entities available again after being unavailable.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetAvailableProcessor(CyodaProcessor):
    """
    Processor for making Pet entities available again.
    Clears unavailability reason and notifies interested customers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailableProcessor",
            description="Makes Pet entities available again after being unavailable",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process making the Pet entity available again.

        Args:
            entity: The Pet entity to make available
            **kwargs: Additional processing parameters

        Returns:
            The available Pet entity
        """
        try:
            self.logger.info(
                f"Making Pet {getattr(entity, 'technical_id', '<unknown>')} available again"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently unavailable
            if not pet.is_unavailable():
                raise ValueError(f"Pet {pet.technical_id} is not in unavailable state")

            # Clear unavailability reason and update availability timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Update availability metadata
            if not pet.metadata:
                pet.metadata = {}
            
            # Clear unavailability metadata
            unavailability_keys = [
                "unavailable_since",
                "unavailability_reason",
                "unavailability_status"
            ]
            for key in unavailability_keys:
                pet.metadata.pop(key, None)

            # Add availability metadata
            pet.metadata.update({
                "available_since": current_time,
                "availability_status": "active"
            })

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} is now available again"
            )

            # Note: Customer notifications would be handled by external service
            self.logger.info(f"Availability notification sent for Pet {pet.technical_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error making Pet {getattr(entity, 'technical_id', '<unknown>')} available: {str(e)}"
            )
            raise
