"""
PetValidationProcessor for Purrfect Pets API

Validates pet data and sets up initial state according to processors.md specification.
"""

import logging
from datetime import date
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetValidationProcessor(CyodaProcessor):
    """
    Processor for Pet validation that handles initial pet data validation
    and sets default values for missing optional fields.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationProcessor",
            description="Validates pet data and sets up initial state",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated pet entity
        """
        try:
            self.logger.info(
                f"Validating Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet name is not empty
            if not pet.name or len(pet.name.strip()) == 0:
                raise ValueError("Pet name is required and cannot be empty")

            # Validate photo URLs is not empty
            if not pet.photo_urls or len(pet.photo_urls) == 0:
                raise ValueError("At least one photo URL is required")

            # Validate category exists (basic check)
            if not pet.category:
                raise ValueError("Pet category is required")

            # Validate price is positive
            if pet.price is not None and pet.price <= 0:
                raise ValueError("Pet price must be positive")

            # Validate birth date is not in future
            if pet.birth_date is not None and pet.birth_date > date.today():
                raise ValueError("Pet birth date cannot be in the future")

            # Set default values for missing optional fields
            if pet.description is None:
                pet.description = f"Beautiful {pet.name}"

            if pet.vaccinated is None:
                pet.vaccinated = False

            if pet.neutered is None:
                pet.neutered = False

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} validated successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error validating pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
