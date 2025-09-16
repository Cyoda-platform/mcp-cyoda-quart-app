"""
PetReleaseProcessor for Purrfect Pets API

Handles the release of Pet entities when reservations are cancelled or expired.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReleaseProcessor(CyodaProcessor):
    """
    Processor for releasing Pet entities from pending state.
    Removes reservation records and makes pet available again.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReleaseProcessor",
            description="Releases Pet entities from pending state and makes them available again",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity release.

        Args:
            entity: The Pet entity to release
            **kwargs: Additional processing parameters

        Returns:
            The released Pet entity
        """
        try:
            self.logger.info(
                f"Releasing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently pending
            if not pet.is_pending():
                raise ValueError(f"Pet {pet.technical_id} is not in pending state")

            # Remove reservation record
            if pet.metadata:
                # Clear reservation-related metadata
                reservation_keys = [
                    "reservation_time",
                    "reservation_expiry", 
                    "reservation_status"
                ]
                for key in reservation_keys:
                    pet.metadata.pop(key, None)

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} released successfully"
            )

            # Note: Release notification would be handled by external service
            self.logger.info(f"Release notification sent for Pet {pet.technical_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error releasing Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
