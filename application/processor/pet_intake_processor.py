"""
PetIntakeProcessor for Purrfect Pets API

Processes a new pet entering the system, validates data, assigns ID, sets arrival date.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetIntakeProcessor(CyodaProcessor):
    """
    Processor for Pet intake that handles new pets entering the system.
    Validates data, sets arrival date, and prepares pet for availability.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetIntakeProcessor",
            description="Processes new pets entering the system, validates data and sets arrival date",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet intake according to functional requirements.

        Args:
            entity: The Pet entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity with arrival date set
        """
        try:
            self.logger.info(
                f"Processing Pet intake for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet data (name, category, breed required)
            self._validate_pet_data(pet)

            # Set arrival date to current timestamp
            pet.set_arrival_date()

            # Validate age is positive (already done in Pet model validation)
            # Validate weight is positive if provided (already done in Pet model validation)

            # Set default values for boolean fields if not provided
            if pet.vaccinated is None:
                pet.vaccinated = False
            if pet.neutered is None:
                pet.neutered = False
            if pet.microchipped is None:
                pet.microchipped = False

            # Log intake completion
            self.logger.info(
                f"Pet {pet.technical_id} intake processed successfully - arrival date set"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet intake {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_pet_data(self, pet: Pet) -> None:
        """
        Validate pet data according to functional requirements.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Name, category, breed are required (validated by Pydantic model)
        if not pet.name or len(pet.name.strip()) == 0:
            raise ValueError("Pet name is required")

        if not pet.category or len(pet.category.strip()) == 0:
            raise ValueError("Pet category is required")

        if not pet.breed or len(pet.breed.strip()) == 0:
            raise ValueError("Pet breed is required")

        # Age must be positive (validated by Pydantic model)
        if pet.age < 0:
            raise ValueError("Pet age must be non-negative")

        # Weight must be positive if provided (validated by Pydantic model)
        if pet.weight <= 0:
            raise ValueError("Pet weight must be positive")

        self.logger.debug(f"Pet data validation passed for {pet.name}")
