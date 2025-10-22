"""
PetValidationCriterion for Cyoda Client Application

Validates that a Pet meets all required business rules before it can
proceed to the processing stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet import Pet


class PetValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet that checks all business rules
    before the entity can proceed to processing stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationCriterion",
            description="Validates Pet business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            pet = cast_entity(entity, Pet)

            if not pet.name or len(pet.name.strip()) == 0:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid name"
                )
                return False

            if not pet.pet_type or len(pet.pet_type.strip()) == 0:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid pet type"
                )
                return False

            allowed_statuses = ["available", "pending", "sold"]
            if pet.status and pet.status not in allowed_statuses:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid status: {pet.status}"
                )
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

