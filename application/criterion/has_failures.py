"""
HasFailuresCriterion for Cyoda Client Application

Checks if any items in an HNItemCollection failed processing 
as specified in workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitemcollection.version_1.hnitemcollection import HNItemCollection


class HasFailuresCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if any items in a collection failed processing.
    
    Checks if failed_items > 0.
    """

    def __init__(self) -> None:
        super().__init__(
            name="has_failures",
            description="Checks if any items failed processing"
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if any items in the collection failed processing.

        Args:
            entity: The CyodaEntity to check (expected to be HNItemCollection)
            **kwargs: Additional criteria parameters

        Returns:
            True if any items failed processing, False otherwise
        """
        try:
            self.logger.info(
                f"Checking for processing failures in entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Check if there are any failures
            has_failures = collection.has_failures()

            if has_failures:
                self.logger.info(
                    f"HNItemCollection {collection.technical_id} has processing failures. "
                    f"Failed items: {collection.failed_items}, Total: {collection.total_items}"
                )
                
                # Log error details if available
                if collection.error_details:
                    self.logger.info(
                        f"Error details for {len(collection.error_details)} failed items available"
                    )
            else:
                self.logger.info(
                    f"HNItemCollection {collection.technical_id} has no processing failures. "
                    f"Total: {collection.total_items}, Processed: {collection.processed_items}"
                )

            return has_failures

        except Exception as e:
            self.logger.error(
                f"Error checking for processing failures in entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
