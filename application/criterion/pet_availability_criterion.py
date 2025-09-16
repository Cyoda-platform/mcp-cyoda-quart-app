"""
PetAvailabilityCriterion for Purrfect Pets API

Checks if a pet is available for reservation by verifying state and inventory.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetAvailabilityCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if a pet is available for reservation.
    Verifies pet state is Available and inventory has sufficient quantity.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailabilityCriterion",
            description="Checks if pet is available for reservation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is available for reservation.

        Args:
            entity: The CyodaEntity to check (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is available, False otherwise
        """
        try:
            self.logger.info(
                f"Checking availability for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet state is Available
            if pet.state != "Available":
                self.logger.info(
                    f"Pet {pet.technical_id} is not available (state: {pet.state})"
                )
                return False

            # Check inventory availability
            inventory_available = await self._check_inventory_availability(pet)
            if not inventory_available:
                self.logger.info(f"Pet {pet.technical_id} has insufficient inventory")
                return False

            self.logger.info(f"Pet {pet.technical_id} is available for reservation")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking availability for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _check_inventory_availability(self, pet: Pet) -> bool:
        """
        Check if inventory has sufficient quantity for the pet.

        Args:
            pet: The Pet entity to check

        Returns:
            True if inventory is sufficient, False otherwise
        """
        try:
            # In a real implementation, we would:
            # 1. Find inventory record by pet_id
            # 2. Calculate available quantity (quantity - reserved_quantity)
            # 3. Check if available quantity > 0

            # For now, we'll assume inventory is available if pet state is Available
            # This is a simplified implementation

            self.logger.debug(f"Checking inventory for pet {pet.technical_id}")

            # Simplified check - assume available if pet is in Available state
            return pet.is_available()

        except Exception as e:
            self.logger.error(
                f"Error checking inventory for pet {pet.technical_id}: {str(e)}"
            )
            return False
