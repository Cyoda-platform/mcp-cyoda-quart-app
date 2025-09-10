"""
ExampleEntityValidationCriterion for Cyoda Client Application

Validates that an ExampleEntity meets all required business rules before it can
proceed to the processing stage as specified in functional requirements.
"""

from common.processor.base import CyodaCriteriaChecker
from entity.example_entity import ExampleEntity


class ExampleEntityValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for ExampleEntity that checks all business rules
    before the entity can proceed to processing stage.
    """

    def __init__(self):
        super().__init__(
            name="ExampleEntityValidationCriterion",
            description="Validates ExampleEntity business rules and data consistency",
        )

    async def check(self, entity: ExampleEntity, **kwargs) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The ExampleEntity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(f"Validating ExampleEntity {entity.technical_id}")

            # Validate required fields are present and valid
            if not entity.name:
                self.logger.warning(f"Entity {entity.technical_id} has invalid name")
                return False

            self.logger.info(f"Entity {entity.technical_id} passed all validation criteria")
            return True

        except Exception as e:
            self.logger.error(f"Error validating entity {entity.technical_id}: {str(e)}")
            return False