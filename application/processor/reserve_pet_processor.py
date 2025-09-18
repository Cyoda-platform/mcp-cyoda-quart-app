"""
ReservePetProcessor for Cyoda Client Application

Handles the reservation of Pet instances when they are reserved for sale.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReservePetProcessor(CyodaProcessor):
    """
    Processor for reserving Pet entities when they are marked as pending sale.
    Sets reserved date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReservePetProcessor",
            description="Reserves Pet instances by setting reserved date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reserve the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters

        Returns:
            The reserved pet with reserved date set
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set reserved date and update timestamp
            pet.set_reserved_date()

            self.logger.info(f"Pet {pet.technical_id} reserved successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
