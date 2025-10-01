"""
PetValidationCriterion for Cyoda Petstore Application

Validates that a Pet entity meets all required business rules before it can
proceed to the processing stage. Ensures data integrity and business logic compliance.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet entity that checks all business rules
    before the entity can proceed to processing stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationCriterion",
            description="Validates Pet business rules and data consistency",
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

            # Validate business logic rules
            if not self._validate_business_rules(pet):
                return False

            # Validate data consistency
            if not self._validate_data_consistency(pet):
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
        """
        Validate required fields are present and valid.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate name
        if not pet.name or len(pet.name.strip()) < 2:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid name: '{pet.name}'"
            )
            return False

        if len(pet.name) > 50:
            self.logger.warning(
                f"Pet {pet.technical_id} name too long: {len(pet.name)} characters"
            )
            return False

        # Validate status
        if pet.status and pet.status not in Pet.ALLOWED_STATUSES:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid status: {pet.status}"
            )
            return False

        # Validate breed if provided
        if pet.breed and pet.breed not in Pet.ALLOWED_BREEDS:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid breed: {pet.breed}"
            )
            return False

        return True

    def _validate_business_rules(self, pet: Pet) -> bool:
        """
        Validate business logic rules.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if all business rules are satisfied, False otherwise
        """
        # Sold pets should have zero or minimal inventory
        if pet.status == "sold" and pet.inventory_count and pet.inventory_count > 0:
            self.logger.warning(
                f"Pet {pet.technical_id} is sold but has inventory count: {pet.inventory_count}"
            )
            return False

        # Pending pets should have reasonable inventory limits
        if pet.status == "pending" and pet.inventory_count and pet.inventory_count > 10:
            self.logger.warning(
                f"Pet {pet.technical_id} is pending but has excessive inventory: {pet.inventory_count}"
            )
            return False

        # Available pets should have positive inventory
        if pet.status == "available" and (
            not pet.inventory_count or pet.inventory_count <= 0
        ):
            self.logger.warning(
                f"Pet {pet.technical_id} is available but has no inventory: {pet.inventory_count}"
            )
            return False

        # Age validation
        if pet.age is not None:
            if pet.age < 0 or pet.age > 30:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid age: {pet.age}"
                )
                return False

        # Price validation
        if pet.price is not None:
            if pet.price < 0 or pet.price > 10000:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid price: {pet.price}"
                )
                return False

        return True

    def _validate_data_consistency(self, pet: Pet) -> bool:
        """
        Validate data consistency across fields.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # Validate inventory count consistency
        if pet.inventory_count is not None:
            if pet.inventory_count < 0 or pet.inventory_count > 1000:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid inventory count: {pet.inventory_count}"
                )
                return False

        # Validate photo URLs if provided
        if pet.photo_urls:
            for url in pet.photo_urls:
                if not isinstance(url, str) or len(url.strip()) == 0:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid photo URL: {url}"
                    )
                    return False

        # Validate category structure if provided
        if pet.category:
            if not isinstance(pet.category, dict):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid category structure"
                )
                return False

            if "name" in pet.category and not pet.category["name"]:
                self.logger.warning(f"Pet {pet.technical_id} has empty category name")
                return False

        # Validate tags structure if provided
        if pet.tags:
            if not isinstance(pet.tags, list):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid tags structure"
                )
                return False

            for tag in pet.tags:
                if not isinstance(tag, dict) or "name" not in tag:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid tag structure: {tag}"
                    )
                    return False

        return True
