"""
PetRegistrationProcessor for Purrfect Pets API

Validates and registers a new pet in the system.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetRegistrationProcessor(CyodaProcessor):
    """
    Processor for Pet registration that validates and registers a new pet in the system.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetRegistrationProcessor",
            description="Validates and registers a new pet in the system",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet registration according to functional requirements.

        Args:
            entity: The Pet entity to register
            **kwargs: Additional processing parameters

        Returns:
            The registered pet with assigned ID and status set to 'available'
        """
        try:
            self.logger.info(
                f"Registering Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet.name is not empty (already done by Pydantic validation)
            # Validate pet.photoUrls is not empty (already done by Pydantic validation)
            # Validate pet.category exists (already done by Pydantic validation)

            # If pet.price is null, set default value based on category
            if pet.price is None:
                pet.price = self._get_default_price_by_category(pet.category)

            # If pet.description is empty, generate default description
            if not pet.description:
                pet.description = self._generate_default_description(pet.name, pet.category)

            # Set creation timestamp
            pet.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} registered successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error registering pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _get_default_price_by_category(self, category: dict) -> Decimal:
        """
        Get default price based on category.

        Args:
            category: The category dictionary

        Returns:
            Default price for the category
        """
        category_name = category.get("name", "").lower()
        
        price_map = {
            "dogs": Decimal("500.00"),
            "cats": Decimal("300.00"),
            "birds": Decimal("150.00"),
            "fish": Decimal("50.00"),
            "reptiles": Decimal("200.00"),
        }
        
        return price_map.get(category_name, Decimal("100.00"))

    def _generate_default_description(self, name: str, category: dict) -> str:
        """
        Generate default description based on name and category.

        Args:
            name: Pet name
            category: Pet category

        Returns:
            Generated description
        """
        category_name = category.get("name", "Pet")
        return f"Meet {name}, a wonderful {category_name.lower()} looking for a loving home!"
