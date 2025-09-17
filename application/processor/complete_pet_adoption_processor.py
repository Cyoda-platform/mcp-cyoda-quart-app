"""
CompleteAdoptionProcessor for Pet entities in Purrfect Pets Application

Handles finalization of pet adoption process.
Marks pets as adopted and updates adoption status.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CompleteAdoptionProcessor(CyodaProcessor):
    """
    Processor for completing Pet adoption process.
    Marks pets as adopted and finalizes adoption details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteAdoptionProcessor",
            description="Finalize pet adoption process",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Complete the Pet adoption according to functional requirements.

        Args:
            entity: The Pet entity to complete adoption for
            **kwargs: Additional processing parameters

        Returns:
            The adopted pet entity
        """
        try:
            self.logger.info(
                f"Completing adoption for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet can complete adoption
            self._validate_pet_for_adoption_completion(pet)

            # Complete the adoption
            self._complete_pet_adoption(pet)

            self.logger.info(f"Pet {pet.technical_id} adoption completed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error completing adoption for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_pet_for_adoption_completion(self, pet: Pet) -> None:
        """
        Validate that pet adoption can be completed.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If adoption cannot be completed
        """
        if not pet.is_reserved():
            raise ValueError(
                f"Pet {pet.name} is not reserved for adoption (current state: {pet.state})"
            )

        # Check if pet has adoption process linked
        if pet.adoption_id is None:
            self.logger.warning(
                f"Pet {pet.name} has no adoption_id linked during completion"
            )

        self.logger.info(f"Pet {pet.name} validation passed for adoption completion")

    def _complete_pet_adoption(self, pet: Pet) -> None:
        """
        Complete the pet adoption according to functional requirements.

        Args:
            pet: The Pet entity to complete adoption for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Update adoption metadata
        pet.add_metadata("status", "adopted")
        pet.add_metadata("adoption_date", current_timestamp)
        pet.add_metadata("available_for_adoption", False)
        pet.add_metadata("completed_by", "CompleteAdoptionProcessor")

        # Clear reservation metadata since adoption is complete
        if pet.metadata and "reservation_expires" in pet.metadata:
            del pet.metadata["reservation_expires"]
        if pet.metadata and "reserved_date" in pet.metadata:
            del pet.metadata["reserved_date"]

        self.logger.info(f"Pet {pet.name} adoption completed on {current_timestamp}")
