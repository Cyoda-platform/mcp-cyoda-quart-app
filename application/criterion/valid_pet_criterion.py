"""
ValidPetCriterion for Purrfect Pets API

Validates that a Pet entity meets all required business rules before it can
proceed to state transitions as specified in the Pet workflow requirements.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidPetCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet entities that checks all business rules
    before the entity can proceed to state transitions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidPetCriterion",
            description="Validates Pet business rules and data consistency",
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
                f"Validating pet entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate required fields
            if not self._validate_required_fields(pet):
                return False

            # Validate business rules
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
                f"Error validating pet entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, pet: Pet) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate name
        if not pet.name or len(pet.name.strip()) == 0:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid name: '{pet.name}'"
            )
            return False

        # Validate photo URLs
        if not pet.photoUrls or len(pet.photoUrls) == 0:
            self.logger.warning(f"Pet {pet.technical_id} has no photo URLs")
            return False

        for url in pet.photoUrls:
            if not url or len(url.strip()) == 0:
                self.logger.warning(f"Pet {pet.technical_id} has empty photo URL")
                return False

        self.logger.debug(f"Required fields validated for pet {pet.technical_id}")
        return True

    def _validate_business_rules(self, pet: Pet) -> bool:
        """
        Validate business rules for the pet.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if business rules are satisfied, False otherwise
        """
        # Validate price is positive if set
        if pet.price is not None and pet.price <= 0:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid price: {pet.price}"
            )
            return False

        # Validate age is reasonable if set
        if pet.age is not None and (pet.age < 0 or pet.age > 300):
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid age: {pet.age} months"
            )
            return False

        # Validate category structure if provided
        if pet.category:
            if not isinstance(pet.category, dict):
                self.logger.warning(
                    f"Pet {pet.technical_id} has invalid category structure"
                )
                return False

            if "id" not in pet.category or "name" not in pet.category:
                self.logger.warning(
                    f"Pet {pet.technical_id} category missing required fields"
                )
                return False

        # Validate tags structure if provided
        if pet.tags:
            for tag in pet.tags:
                if not isinstance(tag, dict):
                    self.logger.warning(
                        f"Pet {pet.technical_id} has invalid tag structure"
                    )
                    return False

                if "id" not in tag or "name" not in tag:
                    self.logger.warning(
                        f"Pet {pet.technical_id} tag missing required fields"
                    )
                    return False

        self.logger.debug(f"Business rules validated for pet {pet.technical_id}")
        return True

    def _validate_data_consistency(self, pet: Pet) -> bool:
        """
        Validate data consistency and state-specific requirements.

        Args:
            pet: The Pet entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # For pets transitioning to pending, ensure basic info is complete
        if pet.state == "available":
            # Pets should have a price set before being available
            if pet.price is None or pet.price <= 0:
                self.logger.warning(
                    f"Pet {pet.technical_id} is available but has no valid price"
                )
                return False

        # For reserved pets, check reservation details
        if pet.state == "pending":
            if not pet.reservedAt:
                self.logger.warning(
                    f"Pet {pet.technical_id} is pending but has no reservation timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

        # For sold pets, check sale details
        if pet.state == "sold":
            if not pet.soldAt:
                self.logger.warning(
                    f"Pet {pet.technical_id} is sold but has no sale timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

        self.logger.debug(f"Data consistency validated for pet {pet.technical_id}")
        return True
