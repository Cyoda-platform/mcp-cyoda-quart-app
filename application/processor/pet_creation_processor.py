"""
PetCreationProcessor for Purrfect Pets Application

Handles the initialization of new pet records and sets up basic information
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetCreationProcessor(CyodaProcessor):
    """
    Processor for initializing new Pet entities.
    Sets default values and validates required fields.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetCreationProcessor",
            description="Initialize a new pet record and set up basic information"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity during creation.

        Args:
            entity: The Pet entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed Pet entity with initialized data
        """
        try:
            self.logger.info(
                f"Processing Pet creation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate required fields
            if not pet.name or len(pet.name.strip()) == 0:
                raise ValueError("Pet name is required")
            
            if not pet.photo_urls or len(pet.photo_urls) == 0:
                raise ValueError("At least one photo URL is required")

            # Set default values for optional fields
            if pet.price is None:
                pet.price = Decimal("0.00")  # Default price, will be updated later
            
            if pet.age is None:
                pet.age = 12  # Default to 1 year old
            
            if pet.gender is None:
                pet.gender = "UNKNOWN"
            
            if pet.vaccinated is None:
                pet.vaccinated = False
            
            if pet.neutered is None:
                pet.neutered = False

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            pet.created_at = current_time
            pet.updated_at = current_time

            self.logger.info(f"Pet creation processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet creation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
