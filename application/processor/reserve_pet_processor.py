"""
ReservePetProcessor for Purrfect Pets Application

Handles reservation of pets for specific adoption processes.
Marks pets as reserved and sets reservation details.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class ReservePetProcessor(CyodaProcessor):
    """
    Processor for reserving Pet entities during adoption process.
    Marks pets as reserved and sets reservation details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReservePetProcessor",
            description="Reserve pet for specific adoption process",
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
            The reserved pet entity
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet can be reserved
            self._validate_pet_for_reservation(pet)

            # Reserve the pet
            self._reserve_pet(pet)

            self.logger.info(
                f"Pet {pet.technical_id} reserved successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_pet_for_reservation(self, pet: Pet) -> None:
        """
        Validate that pet can be reserved.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If pet cannot be reserved
        """
        if not pet.is_available_for_adoption():
            raise ValueError(f"Pet {pet.name} is not available for reservation (current state: {pet.state})")

        if pet.owner_id is not None:
            raise ValueError(f"Pet {pet.name} already has an owner assigned")

        self.logger.info(f"Pet {pet.name} validation passed for reservation")

    def _reserve_pet(self, pet: Pet) -> None:
        """
        Reserve the pet according to functional requirements.

        Args:
            pet: The Pet entity to reserve
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        
        # Calculate reservation expiry (7 days from now)
        expiry_date = datetime.now(timezone.utc) + timedelta(days=7)
        expiry_timestamp = expiry_date.isoformat().replace("+00:00", "Z")

        # Add reservation metadata
        pet.add_metadata("status", "reserved")
        pet.add_metadata("reserved_date", current_timestamp)
        pet.add_metadata("reservation_expires", expiry_timestamp)
        pet.add_metadata("reserved_by", "ReservePetProcessor")

        self.logger.info(
            f"Pet {pet.name} reserved until {expiry_timestamp}"
        )
