"""
CancelReservationProcessor for Cyoda Client Application

Handles the cancellation of Pet reservations when they are returned to available status.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CancelReservationProcessor(CyodaProcessor):
    """
    Processor for canceling Pet reservations when they are returned to available status.
    Clears reserved date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CancelReservationProcessor",
            description="Cancels Pet reservations by clearing reserved date and updating timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Cancel the reservation of the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to cancel reservation for
            **kwargs: Additional processing parameters

        Returns:
            The pet with reservation canceled
        """
        try:
            self.logger.info(
                f"Canceling reservation for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Clear reserved date and update timestamp
            pet.clear_reserved_date()

            self.logger.info(
                f"Pet {pet.technical_id} reservation canceled successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error canceling reservation for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
