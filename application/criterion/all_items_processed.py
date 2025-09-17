"""
AllItemsProcessedCriterion for Cyoda Client Application

Checks if all items in an HNItemCollection have been processed successfully 
as specified in workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitemcollection.version_1.hnitemcollection import HNItemCollection


class AllItemsProcessedCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if all items in a collection have been processed successfully.
    
    Checks if processed_items == total_items AND failed_items == 0.
    """

    def __init__(self) -> None:
        super().__init__(
            name="all_items_processed",
            description="Checks if all items processed successfully"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if all items in the collection have been processed successfully.

        Args:
            entity: The CyodaEntity to check (expected to be HNItemCollection)
            **kwargs: Additional criteria parameters

        Returns:
            True if all items processed successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Checking if all items processed for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Check if all items have been processed successfully
            all_processed = collection.all_items_processed_successfully()

            if all_processed:
                self.logger.info(
                    f"HNItemCollection {collection.technical_id} has all items processed successfully. "
                    f"Total: {collection.total_items}, Processed: {collection.processed_items}, Failed: {collection.failed_items}"
                )
            else:
                self.logger.info(
                    f"HNItemCollection {collection.technical_id} does not have all items processed successfully. "
                    f"Total: {collection.total_items}, Processed: {collection.processed_items}, Failed: {collection.failed_items}"
                )

            return all_processed

        except Exception as e:
            self.logger.error(
                f"Error checking if all items processed for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
