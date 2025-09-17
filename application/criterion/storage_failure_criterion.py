"""
StorageFailureCriterion for Cyoda Client Application

Checks if HN item storage failed.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitem.version_1.hnitem import HnItem


class StorageFailureCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if HN item storage failed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="storage_failure_criterion",
            description="Checks if HN item storage failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity storage failed.

        Args:
            entity: The CyodaEntity to check (expected to be HnItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if storage failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking storage failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Check if storage failed
            has_failed = (
                hn_item.storage_status == "failed" 
                or hn_item.storage_error is not None
            )

            self.logger.info(
                f"Storage failure check for HnItem {hn_item.id}: {has_failed}"
            )

            return has_failed

        except Exception as e:
            self.logger.error(
                f"Error checking storage failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
