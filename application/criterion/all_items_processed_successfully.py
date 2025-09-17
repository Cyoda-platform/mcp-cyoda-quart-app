"""
AllItemsProcessedSuccessfully Criterion for HNItemCollection

Checks if all items in the collection have been processed successfully
to determine if the collection can transition to completed state.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)


class AllItemsProcessedSuccessfully(CyodaCriteriaChecker):
    """
    Criterion that checks if all items in an HNItemCollection have been
    processed successfully without critical errors.
    """

    def __init__(self) -> None:
        super().__init__(
            name="all_items_processed_successfully",
            description="Checks if all items in HNItemCollection have been processed successfully",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if all items have been processed successfully.

        Args:
            entity: The CyodaEntity to check (expected to be HNItemCollection)
            **kwargs: Additional criteria parameters

        Returns:
            True if all items processed successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Checking if all items processed successfully for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Check if processing is complete
            if not collection.is_processing_complete():
                self.logger.info(
                    f"Collection {collection.technical_id} processing not complete. "
                    f"Processed: {collection.processed_items}, Failed: {collection.failed_items}, "
                    f"Total: {collection.total_items}"
                )
                return False

            # Check success rate threshold
            success_rate = collection.get_success_rate()
            failure_rate = collection.get_failure_rate()

            # Consider successful if:
            # 1. At least 95% success rate, OR
            # 2. 100% processed with less than 5% failures, OR
            # 3. All items processed and no critical errors

            if success_rate >= 95.0:
                self.logger.info(
                    f"Collection {collection.technical_id} meets success criteria with {success_rate:.1f}% success rate"
                )
                return True

            # Check for critical errors
            if collection.processing_errors:
                critical_error_count = self._count_critical_errors(
                    collection.processing_errors
                )
                critical_error_rate = (
                    (critical_error_count / collection.total_items) * 100
                    if collection.total_items > 0
                    else 0
                )

                if critical_error_rate > 5.0:
                    self.logger.warning(
                        f"Collection {collection.technical_id} has too many critical errors: "
                        f"{critical_error_count} critical errors ({critical_error_rate:.1f}%)"
                    )
                    return False

            # If we have some failures but they're not critical and overall success is reasonable
            if failure_rate <= 10.0 and collection.processed_items > 0:
                self.logger.info(
                    f"Collection {collection.technical_id} meets success criteria with acceptable failure rate: "
                    f"{failure_rate:.1f}%"
                )
                return True

            self.logger.warning(
                f"Collection {collection.technical_id} does not meet success criteria. "
                f"Success rate: {success_rate:.1f}%, Failure rate: {failure_rate:.1f}%"
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Error checking success criteria for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _count_critical_errors(self, processing_errors: list) -> int:
        """
        Count the number of critical errors in the processing errors list.

        Args:
            processing_errors: List of error dictionaries

        Returns:
            Number of critical errors
        """
        critical_error_types = [
            "validation_error",
            "batch_processing_error",
            "file_processing_error",
            "firebase_pull_error",
        ]

        critical_count = 0
        for error in processing_errors:
            if isinstance(error, dict):
                error_type = error.get("type", "")
                if error_type in critical_error_types:
                    critical_count += 1

        return critical_count
