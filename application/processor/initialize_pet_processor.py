"""
InitializePetProcessor for Purrfect Pets Application

Handles initialization of new pets in the system.
Sets up new pet status and validates data.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class InitializePetProcessor(CyodaProcessor):
    """
    Processor for initializing Pet entities.
    Sets up new pet status and validates data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InitializePetProcessor",
            description="Initialize pet status and validate data for new pets",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Initialize the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized pet entity
        """
        try:
            self.logger.info(
                f"Initializing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Initialize pet data
            self._initialize_pet_data(pet)

            # Validate pet data
            self._validate_pet_data(pet)

            self.logger.info(f"Pet {pet.technical_id} initialized successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error initializing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _initialize_pet_data(self, pet: Pet) -> None:
        """
        Initialize pet data according to functional requirements.

        Args:
            pet: The Pet entity to initialize
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add metadata for tracking
        pet.add_metadata("date_added", current_timestamp)
        pet.add_metadata("status", "available")
        pet.add_metadata("initialized_by", "InitializePetProcessor")

        self.logger.info(f"Initialized pet data for {pet.name}")

    def _validate_pet_data(self, pet: Pet) -> None:
        """
        Validate pet data according to functional requirements.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Basic validation - Pydantic handles most field validation
        if not pet.name or len(pet.name.strip()) == 0:
            raise ValueError("Pet name is required")

        if not pet.species or len(pet.species.strip()) == 0:
            raise ValueError("Pet species is required")

        if not pet.breed or len(pet.breed.strip()) == 0:
            raise ValueError("Pet breed is required")

        if pet.age < 0:
            raise ValueError("Pet age cannot be negative")

        if pet.adoption_fee < 0:
            raise ValueError("Adoption fee cannot be negative")

        # Ensure no owner or adoption references during initialization
        if pet.owner_id is not None:
            self.logger.warning(
                f"Pet {pet.technical_id} has owner_id during initialization, clearing it"
            )
            pet.owner_id = None

        if pet.adoption_id is not None:
            self.logger.warning(
                f"Pet {pet.technical_id} has adoption_id during initialization, clearing it"
            )
            pet.adoption_id = None

        self.logger.info(f"Pet data validation passed for {pet.name}")
