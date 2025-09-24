"""
InitializePetProcessor for Purrfect Pets API

Handles the initialization of new pets in the system, setting default values
and validating data as specified in the Pet workflow requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class InitializePetProcessor(CyodaProcessor):
    """
    Processor for initializing Pet entities when they transition from initial_state to available.
    Sets up new pets with default values and validates required data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InitializePetProcessor",
            description="Initialize pet with default values and validate data for listing",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for initialization.

        Args:
            entity: The Pet entity to initialize (must be in 'initial_state')
            **kwargs: Additional processing parameters

        Returns:
            The initialized pet entity ready for listing
        """
        try:
            self.logger.info(
                f"Initializing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate required fields
            self._validate_required_fields(pet)

            # Set default values
            self._set_default_values(pet)

            # Log initialization completion
            self.logger.info(
                f"Pet {pet.technical_id} initialized successfully and ready for listing"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error initializing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_required_fields(self, pet: Pet) -> None:
        """
        Validate that required fields are present and valid.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate name
        if not pet.name or len(pet.name.strip()) == 0:
            raise ValueError("Pet name is required for initialization")

        # Validate photo URLs
        if not pet.photoUrls or len(pet.photoUrls) == 0:
            raise ValueError("At least one photo URL is required for initialization")

        for url in pet.photoUrls:
            if not url or len(url.strip()) == 0:
                raise ValueError("Photo URLs cannot be empty")

        self.logger.debug(f"Required fields validated for pet {pet.name}")

    def _set_default_values(self, pet: Pet) -> None:
        """
        Set default values for the pet entity.

        Args:
            pet: The Pet entity to set defaults for
        """
        current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Set date added
        if not pet.dateAdded:
            pet.dateAdded = current_timestamp

        # Initialize view count
        if pet.viewCount is None:
            pet.viewCount = 0

        # Set default category if not provided
        if not pet.category:
            pet.category = {"id": 1, "name": "General"}

        # Initialize empty tags list if not provided
        if not pet.tags:
            pet.tags = []

        # Set default price if not provided (can be updated later)
        if pet.price is None:
            pet.price = 0.0

        # Update timestamp
        pet.update_timestamp()

        self.logger.debug(
            f"Default values set for pet {pet.name}: "
            f"dateAdded={pet.dateAdded}, viewCount={pet.viewCount}"
        )
