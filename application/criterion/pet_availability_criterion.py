"""
PetAvailabilityCriterion for Purrfect Pets API

Checks if a pet is available for reservation.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet.version_1.pet import Pet


class PetAvailabilityCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a pet is available for reservation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailabilityCriterion",
            description="Checks if a pet is available for reservation",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is available for reservation.

        Args:
            entity: The Pet entity to check
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is available for reservation, False otherwise
        """
        try:
            self.logger.info(
                f"Checking pet availability for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet's current state is AVAILABLE
            if not pet.is_available():
                self.logger.info(
                    f"Pet {pet.technical_id} is not available (current state: {pet.state})"
                )
                return False

            # Additional checks could be added here, such as:
            # - Pet health status
            # - Store capacity
            # - Pet age restrictions
            # For now, we keep it minimal as per requirements

            self.logger.info(
                f"Pet {pet.technical_id} is available for reservation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking pet availability for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
