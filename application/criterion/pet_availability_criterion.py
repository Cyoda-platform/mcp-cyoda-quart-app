"""
PetAvailabilityCriterion for Purrfect Pets API

Checks if pet is available for reservation or purchase according to criteria.md specification.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetAvailabilityCriterion(CyodaCriteriaChecker):
    """
    Availability criterion for Pet that checks if pet is available for reservation or purchase.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailabilityCriterion",
            description="Checks if pet is available for reservation or purchase",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is available for reservation or purchase.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is available, False otherwise
        """
        try:
            self.logger.info(
                f"Checking availability for pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet state is AVAILABLE
            if pet.state != "available":
                self.logger.warning(
                    f"Pet {pet.technical_id} is not in AVAILABLE state, current state: {pet.state}"
                )
                return False

            # Check if pet has active reservations
            if pet.metadata and "reservation" in pet.metadata:
                reservation = pet.metadata["reservation"]
                if isinstance(reservation, dict) and reservation.get("type"):
                    self.logger.warning(
                        f"Pet {pet.technical_id} has active reservation: {reservation.get('type')}"
                    )
                    return False

            # Check if pet is associated with pending orders
            if pet.metadata and "order_associations" in pet.metadata:
                associations = pet.metadata["order_associations"]
                if associations:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has pending order associations"
                    )
                    return False

            self.logger.info(f"Pet {pet.technical_id} passed availability check")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking pet availability {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
