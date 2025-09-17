"""
ProcessingHasCriticalErrors Criterion for HNItemCollection

Checks if the collection processing has encountered critical errors
that would cause it to transition to failed state.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)


class ProcessingHasCriticalErrors(CyodaCriteriaChecker):
    """
    Criterion that checks if an HNItemCollection has encountered critical errors
    during processing that would warrant transitioning to failed state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="processing_has_critical_errors",
            description="Checks if HNItemCollection processing has critical errors",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if processing has critical errors.

        Args:
            entity: The CyodaEntity to check (expected to be HNItemCollection)
            **kwargs: Additional criteria parameters

        Returns:
            True if critical errors exist, False otherwise
        """
        try:
            self.logger.info(
                f"Checking for critical errors in entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Check if there are any processing errors
            if not collection.processing_errors:
                self.logger.info(
                    f"No processing errors found for collection {collection.technical_id}"
                )
                return False

            # Analyze error severity and frequency
            critical_errors = self._identify_critical_errors(
                collection.processing_errors
            )

            if not critical_errors:
                self.logger.info(
                    f"No critical errors found for collection {collection.technical_id}"
                )
                return False

            # Check critical error thresholds
            critical_error_count = len(critical_errors)
            total_items = collection.total_items

            # Consider critical if:
            # 1. More than 50% of items failed with critical errors, OR
            # 2. Validation errors affecting the entire collection, OR
            # 3. System-level errors that prevent processing

            if total_items > 0:
                critical_error_rate = (critical_error_count / total_items) * 100

                if critical_error_rate > 50.0:
                    self.logger.error(
                        f"Collection {collection.technical_id} has critical error rate of {critical_error_rate:.1f}% "
                        f"({critical_error_count} critical errors out of {total_items} items)"
                    )
                    return True

            # Check for system-level critical errors
            system_errors = self._identify_system_errors(critical_errors)
            if system_errors:
                self.logger.error(
                    f"Collection {collection.technical_id} has {len(system_errors)} system-level critical errors"
                )
                return True

            # Check for validation errors that affect the entire collection
            validation_errors = self._identify_validation_errors(critical_errors)
            if (
                validation_errors and len(validation_errors) >= 3
            ):  # Multiple validation issues
                self.logger.error(
                    f"Collection {collection.technical_id} has {len(validation_errors)} validation errors"
                )
                return True

            self.logger.info(
                f"Collection {collection.technical_id} has {critical_error_count} critical errors "
                f"but does not meet failure threshold"
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Error checking critical errors for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # In case of error checking, assume critical error exists for safety
            return True

    def _identify_critical_errors(self, processing_errors: list) -> list:
        """
        Identify critical errors from the processing errors list.

        Args:
            processing_errors: List of error dictionaries

        Returns:
            List of critical error dictionaries
        """
        critical_error_types = [
            "validation_error",
            "batch_processing_error",
            "file_processing_error",
            "firebase_pull_error",
            "system_error",
            "database_error",
            "network_error",
        ]

        critical_errors = []
        for error in processing_errors:
            if isinstance(error, dict):
                error_type = error.get("type", "")
                if error_type in critical_error_types:
                    critical_errors.append(error)

        return critical_errors

    def _identify_system_errors(self, critical_errors: list) -> list:
        """
        Identify system-level errors that prevent processing.

        Args:
            critical_errors: List of critical error dictionaries

        Returns:
            List of system error dictionaries
        """
        system_error_types = [
            "batch_processing_error",
            "system_error",
            "database_error",
            "network_error",
        ]

        system_errors = []
        for error in critical_errors:
            error_type = error.get("type", "")
            if error_type in system_error_types:
                system_errors.append(error)

        return system_errors

    def _identify_validation_errors(self, critical_errors: list) -> list:
        """
        Identify validation errors that affect collection structure.

        Args:
            critical_errors: List of critical error dictionaries

        Returns:
            List of validation error dictionaries
        """
        validation_errors = []
        for error in critical_errors:
            error_type = error.get("type", "")
            if error_type in ["validation_error", "file_processing_error"]:
                validation_errors.append(error)

        return validation_errors
