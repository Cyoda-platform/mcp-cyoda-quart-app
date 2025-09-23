"""
PetValidationCriterion for Cyoda Pet Search Application

Validates that a Pet entity meets all required business rules before it can
proceed to the transformation stage as specified in functional requirements.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet entity that checks all business rules
    before the entity can proceed to transformation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationCriterion",
            description="Validates Pet business rules and data consistency for search application",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet entity meets all validation criteria.

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
        """Validate that all required fields are present and valid."""

        # Validate name
        if not pet.name or len(pet.name.strip()) == 0:
            self.logger.warning(f"Pet {pet.technical_id} has empty or missing name")
            return False

        if len(pet.name) > 100:
            self.logger.warning(
                f"Pet {pet.technical_id} has name too long: {len(pet.name)} characters"
            )
            return False

        # Validate status
        allowed_statuses = ["available", "pending", "sold"]
        if pet.status not in allowed_statuses:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid status: {pet.status}"
            )
            return False

        # Validate photo URLs for available pets
        if pet.status == "available" and not pet.photo_urls:
            self.logger.warning(
                f"Pet {pet.technical_id} is available but has no photo URLs"
            )
            return False

        return True

    def _validate_business_rules(self, pet: Pet) -> bool:
        """Validate business logic rules specific to pet search application."""

        # Rule 1: Available pets must have at least one photo
        if pet.status == "available" and (
            not pet.photo_urls or len(pet.photo_urls) == 0
        ):
            self.logger.warning(
                f"Pet {pet.technical_id} is available but has no photos"
            )
            return False

        # Rule 2: Pet must have either category or tags for species identification
        has_category = (
            pet.category and isinstance(pet.category, dict) and pet.category.get("name")
        )
        has_tags = pet.tags and len(pet.tags) > 0

        if not has_category and not has_tags:
            self.logger.warning(
                f"Pet {pet.technical_id} has no category or tags for species identification"
            )
            return False

        # Rule 3: If search parameters are provided, they should be valid
        if pet.search_species:
            allowed_species = [
                "dog",
                "cat",
                "bird",
                "fish",
                "rabbit",
                "hamster",
                "other",
            ]
            if pet.search_species not in allowed_species:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid search species: {pet.search_species}"
                )
                return False

        if pet.search_status:
            if pet.search_status not in ["available", "pending", "sold"]:
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid search status: {pet.search_status}"
                )
                return False

        return True

    def _validate_data_consistency(self, pet: Pet) -> bool:
        """Validate data consistency and logical relationships."""

        # Check if ingested data is present (should be set by ingestion processor)
        if not pet.ingested_at:
            self.logger.warning(
                f"Pet {pet.technical_id} has no ingestion timestamp - data may not be properly ingested"
            )
            return False

        # Validate category structure if present
        if pet.category:
            if not isinstance(pet.category, dict):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid category format"
                )
                return False

            # Category should have at least a name
            if "name" not in pet.category or not pet.category["name"]:
                self.logger.warning(f"Pet {pet.technical_id} has category without name")
                return False

        # Validate tags structure if present
        if pet.tags:
            if not isinstance(pet.tags, list):
                self.logger.warning(f"Pet {pet.technical_id} has invalid tags format")
                return False

            for i, tag in enumerate(pet.tags):
                if not isinstance(tag, dict):
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid tag format at index {i}"
                    )
                    return False

        # Validate photo URLs format
        if pet.photo_urls:
            if not isinstance(pet.photo_urls, list):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid photo URLs format"
                )
                return False

            for i, url in enumerate(pet.photo_urls):
                if not isinstance(url, str) or len(url.strip()) == 0:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid photo URL at index {i}"
                    )
                    return False

        # Check consistency between search parameters and actual data
        if pet.search_status and pet.status and pet.search_status != pet.status:
            self.logger.info(
                f"Pet {pet.technical_id} search status ({pet.search_status}) differs from actual status ({pet.status}) - this is acceptable"
            )

        return True
