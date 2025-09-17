"""
ValidationFailureCriterion for Cyoda Client Application

Checks if HN item validation failed.
"""

from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidationFailureCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if HN item validation failed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validation_failure_criterion",
            description="Checks if HN item validation failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity validation failed.

        Args:
            entity: The CyodaEntity to check (expected to be HnItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if validation failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking validation failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Check if validation failed
            has_failed = hn_item.validation_status == "failed" or (
                hn_item.validation_errors and len(hn_item.validation_errors) > 0
            )

            self.logger.info(
                f"Validation failure check for HnItem {hn_item.id}: {has_failed}"
            )

            return has_failed

        except Exception as e:
            self.logger.error(
                f"Error checking validation failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
