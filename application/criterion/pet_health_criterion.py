"""
PetHealthCriterion for Purrfect Pets API

Validates pet health status before making available according to criteria.md specification.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetHealthCriterion(CyodaCriteriaChecker):
    """
    Health criterion for Pet that validates pet health status before making available.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetHealthCriterion",
            description="Validates pet health status before making available",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet meets health requirements.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is healthy, False otherwise
        """
        try:
            self.logger.info(
                f"Checking health status for pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is vaccinated
            if pet.vaccinated is False:
                self.logger.warning(f"Pet {pet.technical_id} is not vaccinated")
                return False

            # Check if pet has health issues recorded
            if pet.metadata and "health_issues" in pet.metadata:
                health_issues = pet.metadata["health_issues"]
                if health_issues:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has recorded health issues: {health_issues}"
                    )
                    return False

            # Check if pet requires medical attention
            if pet.metadata and "medical_attention_required" in pet.metadata:
                medical_attention = pet.metadata["medical_attention_required"]
                if medical_attention is True:
                    self.logger.warning(
                        f"Pet {pet.technical_id} requires medical attention"
                    )
                    return False

            self.logger.info(f"Pet {pet.technical_id} passed health check")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking pet health {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
