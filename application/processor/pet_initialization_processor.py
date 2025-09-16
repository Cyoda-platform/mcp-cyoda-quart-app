"""
PetInitializationProcessor for Purrfect Pets API

Handles the initialization of Pet entities when they are first created.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetInitializationProcessor(CyodaProcessor):
    """
    Processor for initializing Pet entities.
    Sets default values and prepares the pet for availability.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetInitializationProcessor",
            description="Initializes Pet entities with default values and prepares them for availability",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity initialization.

        Args:
            entity: The Pet entity to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized Pet entity
        """
        try:
            self.logger.info(
                f"Initializing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set default values for optional fields if not provided
            if not pet.photo_urls:
                pet.photo_urls = []

            if not pet.tags:
                pet.tags = []

            # Set created_at timestamp if not already set
            if not pet.created_at:
                pet.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Initialize photo_urls as empty list if not provided
            if pet.photo_urls is None:
                pet.photo_urls = []

            # Validate pet data
            if not pet.name or len(pet.name.strip()) == 0:
                raise ValueError("Pet name is required")

            if pet.category_id <= 0:
                raise ValueError("Valid category_id is required")

            if pet.price <= 0:
                raise ValueError("Pet price must be greater than 0")

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} initialized successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error initializing Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
