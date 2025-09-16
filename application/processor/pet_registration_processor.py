"""
PetRegistrationProcessor for Purrfect Pets API

Validates and registers a new pet in the system, creating associated inventory record.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.inventory.version_1.inventory import Inventory
from services.services import get_entity_service


class PetRegistrationProcessor(CyodaProcessor):
    """
    Processor for registering new pets in the system.
    Validates pet data and creates associated inventory record.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetRegistrationProcessor",
            description="Validates and registers new pets, creates inventory record",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet registration according to functional requirements.

        Args:
            entity: The Pet entity to register
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet registration {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet data
            self._validate_pet_data(pet)

            # Update timestamps
            pet.update_timestamp()

            # Create inventory record for the pet
            await self._create_inventory_record(pet)

            self.logger.info(f"Pet {pet.technical_id} registered successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_pet_data(self, pet: Pet) -> None:
        """
        Validate pet data according to functional requirements.

        Args:
            pet: The Pet entity to validate
        """
        # Validate name
        if not pet.name or len(pet.name.strip()) == 0:
            raise ValueError("Pet name is required")
        if len(pet.name) > 100:
            raise ValueError("Pet name must be at most 100 characters")

        # Validate category_id exists (basic validation)
        if pet.category_id <= 0:
            raise ValueError("Valid category_id is required")

        # Validate price
        if pet.price < 0:
            raise ValueError("Pet price must be non-negative")

        # Validate age
        if pet.age < 0 or pet.age > 50:
            raise ValueError("Pet age must be between 0 and 50 years")

        # Validate weight
        if pet.weight <= 0:
            raise ValueError("Pet weight must be positive")

        # Validate photo URLs
        for url in pet.photo_urls:
            if not url.startswith(("http://", "https://")):
                raise ValueError("Photo URLs must be valid HTTP/HTTPS URLs")

    async def _create_inventory_record(self, pet: Pet) -> None:
        """
        Create inventory record for the registered pet.

        Args:
            pet: The registered Pet entity
        """
        try:
            entity_service = get_entity_service()

            # Create inventory record with initial quantity of 1
            inventory = Inventory(
                pet_id=pet.technical_id or pet.entity_id,
                quantity=1,
                reserved_quantity=0,
                reorder_level=1,
            )

            # Convert to dict for EntityService.save()
            inventory_data = inventory.model_dump(by_alias=True)

            # Save the inventory record
            response = await entity_service.save(
                entity=inventory_data,
                entity_class=Inventory.ENTITY_NAME,
                entity_version=str(Inventory.ENTITY_VERSION),
            )

            created_inventory_id = response.metadata.id

            self.logger.info(
                f"Created inventory record {created_inventory_id} for pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create inventory record for pet {pet.technical_id}: {str(e)}"
            )
            # Don't raise here - pet registration should succeed even if inventory creation fails
            # The inventory can be created later manually
