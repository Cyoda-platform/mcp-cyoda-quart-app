"""
StorageSuccessCriterion for Cyoda Client Application

Checks if HN item storage was successful.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitem.version_1.hnitem import HnItem


class StorageSuccessCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if HN item storage was successful.
    """

    def __init__(self) -> None:
        super().__init__(
            name="storage_success_criterion",
            description="Checks if HN item storage was successful",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity storage was successful.

        Args:
            entity: The CyodaEntity to check (expected to be HnItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            self.logger.info(
                f"Checking storage success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Check if storage was successful
            is_successful = (
                hn_item.storage_status == "success" 
                and hn_item.stored_at is not None
            )

            self.logger.info(
                f"Storage success check for HnItem {hn_item.id}: {is_successful}"
            )

            return is_successful

        except Exception as e:
            self.logger.error(
                f"Error checking storage success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
