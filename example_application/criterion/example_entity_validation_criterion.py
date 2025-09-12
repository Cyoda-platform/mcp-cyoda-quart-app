"""
ExampleEntityValidationCriterion for Cyoda Client Application

Validates that an ExampleEntity meets all required business rules before it can
proceed to the processing stage as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
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
            self.logger.info(f"Validating entity {getattr(entity, 'technical_id', '<unknown>')}")

            # Cast the entity to ExampleEntity for type-safe operations
            example_entity = cast_entity(entity, ExampleEntity)

            # State is managed by Cyoda workflow engine - no manual state checks needed

            # Validate required fields
            if (
                not example_entity.name
                or len(example_entity.name.strip()) < 3
                or len(example_entity.name) > 100
            ):
                self.logger.warning(
                    f"Entity {example_entity.technical_id} has invalid name: '{example_entity.name}'"
                )
                return False

            if not example_entity.description or len(example_entity.description) > 500:
                self.logger.warning(f"Entity {example_entity.technical_id} has invalid description")
                return False

            # Validate category
            allowed_categories = ["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"]
            if example_entity.category not in allowed_categories:
                self.logger.warning(
                    f"Entity {example_entity.technical_id} has invalid category: {example_entity.category}"
                )
                return False

            # Validate business logic rules (simplified without numeric constraints)
            if not example_entity.is_active and example_entity.category == "ELECTRONICS":
                self.logger.warning(
                    f"Entity {example_entity.technical_id} ELECTRONICS category entities must be active"
                )
                return False

            self.logger.info(f"Entity {example_entity.technical_id} passed all validation criteria")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
