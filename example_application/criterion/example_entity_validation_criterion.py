"""
ExampleEntityValidationCriterion for Cyoda Client Application

Validates that an ExampleEntity meets all required business rules before it can
proceed to the processing stage as specified in functional requirements.
"""

from typing import Any

from common.processor.base import CyodaCriteriaChecker, CyodaEntity

from example_application.entity.example_entity import ExampleEntity


class ExampleEntityValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for ExampleEntity that checks all business rules
    before the entity can proceed to processing stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ExampleEntityValidationCriterion",
            description="Validates ExampleEntity business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be ExampleEntity)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Ensure we are validating the correct entity type
            if not isinstance(entity, ExampleEntity):
                self.logger.error(
                    "ExampleEntityValidationCriterion received an incompatible entity type: "
                    f"{type(entity).__name__}"
                )
                return False

            # State is managed by Cyoda workflow engine - no manual state checks needed

            # Validate required fields
            if (
                not entity.name
                or len(entity.name.strip()) < 3
                or len(entity.name) > 100
            ):
                self.logger.warning(
                    f"Entity {entity.technical_id} has invalid name: '{entity.name}'"
                )
                return False

            if not entity.description or len(entity.description) > 500:
                self.logger.warning(
                    f"Entity {entity.technical_id} has invalid description"
                )
                return False

            if entity.value <= 0:
                self.logger.warning(
                    f"Entity {entity.technical_id} has invalid value: {entity.value}"
                )
                return False

            # Validate category
            allowed_categories = ["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"]
            if entity.category not in allowed_categories:
                self.logger.warning(
                    f"Entity {entity.technical_id} has invalid category: {entity.category}"
                )
                return False

            # Validate business logic rules
            if entity.category == "ELECTRONICS" and entity.value <= 10:
                self.logger.warning(
                    f"Entity {entity.technical_id} ELECTRONICS category requires value > 10, got {entity.value}"
                )
                return False

            if entity.category == "CLOTHING" and (
                entity.value < 5 or entity.value > 1000
            ):
                self.logger.warning(
                    f"Entity {entity.technical_id} CLOTHING category requires value between 5 and 1000, got {entity.value}"
                )
                return False

            if entity.category == "BOOKS" and (entity.value < 1 or entity.value > 500):
                self.logger.warning(
                    f"Entity {entity.technical_id} BOOKS category requires value between 1 and 500, got {entity.value}"
                )
                return False

            if entity.is_active is False and entity.value >= 100:
                self.logger.warning(
                    f"Entity {entity.technical_id} inactive entities require value < 100, got {entity.value}"
                )
                return False

            self.logger.info(
                f"Entity {entity.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
