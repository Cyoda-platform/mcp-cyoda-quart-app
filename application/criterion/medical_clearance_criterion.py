"""
MedicalClearanceCriterion for Purrfect Pets API

Checks if a pet on medical hold can be cleared.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet.version_1.pet import Pet


class MedicalClearanceCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a pet on medical hold can be cleared.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MedicalClearanceCriterion",
            description="Checks if a pet on medical hold can be cleared",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet can be cleared from medical hold.

        Args:
            entity: The Pet entity to check
            **kwargs: Additional criteria parameters (clearance details)

        Returns:
            True if the pet can be cleared from medical hold, False otherwise
        """
        try:
            self.logger.info(
                f"Checking medical clearance for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet's current state is MEDICAL_HOLD
            if not pet.is_on_medical_hold():
                self.logger.info(
                    f"Pet {pet.technical_id} is not on medical hold (current state: {pet.state})"
                )
                return False

            # Get clearance details from kwargs
            veterinarian_approval = kwargs.get("veterinarianApproval") or kwargs.get("veterinarian_approval")
            treatment_complete = kwargs.get("treatmentComplete") or kwargs.get("treatment_complete")

            # Check if veterinarian approval is provided
            if not veterinarian_approval:
                self.logger.info(
                    f"Pet {pet.technical_id} does not have veterinarian approval"
                )
                return False

            # Check if treatment is complete
            if not treatment_complete:
                self.logger.info(
                    f"Pet {pet.technical_id} treatment is not complete"
                )
                return False

            self.logger.info(
                f"Pet {pet.technical_id} can be cleared from medical hold"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking medical clearance for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
