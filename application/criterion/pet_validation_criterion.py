"""
PetValidationCriterion for Product Performance Analysis and Reporting System

Validates that a Pet entity meets all required business rules before it can
proceed to the analysis stage.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet entity that checks all business rules
    before the entity can proceed to analysis stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationCriterion",
            description="Validates Pet entity business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Pet entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Pet entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate required fields
            if not self._validate_required_fields(pet):
                return False

            # Validate field formats and constraints
            if not self._validate_field_constraints(pet):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(pet):
                return False

            self.logger.info(
                f"Pet entity {pet.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Pet entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, pet: Pet) -> bool:
        """Validate that all required fields are present and valid"""

        # Name is required
        if not pet.name or len(pet.name.strip()) == 0:
            self.logger.warning(f"Pet {pet.technical_id} has empty name")
            return False

        if len(pet.name) > 255:
            self.logger.warning(
                f"Pet {pet.technical_id} name too long: {len(pet.name)} characters"
            )
            return False

        return True

    def _validate_field_constraints(self, pet: Pet) -> bool:
        """Validate field formats and constraints"""

        # Validate status if present
        if pet.status and pet.status not in Pet.VALID_STATUSES:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid status: {pet.status}. "
                f"Valid statuses: {Pet.VALID_STATUSES}"
            )
            return False

        # Validate performance score if present
        if pet.performance_score is not None:
            if pet.performance_score < 0.0 or pet.performance_score > 100.0:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid performance score: {pet.performance_score}. "
                    "Must be between 0.0 and 100.0"
                )
                return False

        # Validate photo URLs format
        if pet.photo_urls:
            for i, url in enumerate(pet.photo_urls):
                if not isinstance(url, str) or len(url.strip()) == 0:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid photo URL at index {i}: {url}"
                    )
                    return False

        return True

    def _validate_business_rules(self, pet: Pet) -> bool:
        """Validate business logic rules"""

        # Business rule: Pets with "sold" status should not have performance analysis
        # (they're no longer available for performance tracking)
        if pet.status == "sold" and pet.performance_score is not None:
            self.logger.warning(
                f"Pet {pet.technical_id} has 'sold' status but has performance score. "
                "Sold pets should not have performance analysis."
            )
            # This is a warning, not a failure - we'll allow it but log it

        # Business rule: Available pets should have complete data for better analysis
        if pet.status == "available":
            completeness_score = self._calculate_data_completeness(pet)
            if completeness_score < 50.0:  # Less than 50% complete
                self.logger.warning(
                    f"Pet {pet.technical_id} is available but has low data completeness: {completeness_score:.1f}%"
                )
                # This is a warning, not a failure - we'll allow it but recommend improvement

        return True

    def _calculate_data_completeness(self, pet: Pet) -> float:
        """Calculate data completeness percentage"""
        total_fields = 5  # name, category, status, photo_urls, tags
        complete_fields = 0

        if pet.name:
            complete_fields += 1
        if pet.category:
            complete_fields += 1
        if pet.status:
            complete_fields += 1
        if pet.photo_urls and len(pet.photo_urls) > 0:
            complete_fields += 1
        if pet.tags and len(pet.tags) > 0:
            complete_fields += 1

        return (complete_fields / total_fields) * 100.0
