"""
ValidationSuccessCriterion for Cyoda Client Application

Checks if HN item validation was successful.
"""

from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidationSuccessCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if HN item validation was successful.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validation_success_criterion",
            description="Checks if HN item validation was successful",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity validation was successful.

        Args:
            entity: The CyodaEntity to check (expected to be HnItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if validation was successful, False otherwise
        """
        try:
            self.logger.info(
                f"Checking validation success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Check if validation was successful
            is_successful = hn_item.validation_status == "passed" and (
                not hn_item.validation_errors or len(hn_item.validation_errors) == 0
            )

            self.logger.info(
                f"Validation success check for HnItem {hn_item.id}: {is_successful}"
            )

            return is_successful

        except Exception as e:
            self.logger.error(
                f"Error checking validation success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
