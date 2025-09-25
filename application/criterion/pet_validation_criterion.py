"""
PetValidationCriterion for Purrfect Pets API Application

Validates that a Pet meets all required business rules before it can
proceed to the processing stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet.version_1.pet import Pet


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
        Check if the pet meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate required fields
            if not pet.name or len(pet.name.strip()) < 2:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid name: '{pet.name}'"
                )
                return False

            # Validate status
            if pet.status not in Pet.ALLOWED_STATUSES:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid status: {pet.status}"
                )
                return False

            # Validate category if provided
            if pet.category_name and pet.category_name not in Pet.ALLOWED_CATEGORIES:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid category: {pet.category_name}"
                )
                return False

            # Validate photo URLs format
            for url in pet.photo_urls:
                if not url.startswith(("http://", "https://")):
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid photo URL: {url}"
                    )
                    return False

            # Business rule: available pets should have at least one photo
            if pet.status == "available" and not pet.photo_urls:
                self.logger.warning(
                    f"Pet {pet.technical_id} is available but has no photos"
                )
                # This is a warning, not a failure - let it proceed to processing
                # where the processor can handle this case

            # Validate age if provided
            if pet.age is not None and (pet.age < 0 or pet.age > 30):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid age: {pet.age}"
                )
                return False

            # Validate price if provided
            if pet.price is not None and pet.price < 0:
                self.logger.warning(
                    f"Pet {pet.technical_id} has negative price: {pet.price}"
                )
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
