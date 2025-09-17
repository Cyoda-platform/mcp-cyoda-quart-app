"""
ValidateCollection Processor for HNItemCollection

Validates that an HNItemCollection has valid structure and data
before batch processing can begin.
"""

import logging
from typing import Any, Dict, List

from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ValidateCollection(CyodaProcessor):
    """
    Processor for validating HNItemCollection structure and data.
    Validates collection type, items format, and data consistency.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validate_collection",
            description="Validates HNItemCollection structure and data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Validate the HNItemCollection structure and data.

        Args:
            entity: The HNItemCollection to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated collection with validation status
        """
        try:
            self.logger.info(
                f"Validating HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            validation_errors = []

            # Validate collection type
            if (
                collection.collection_type
                not in HNItemCollection.ALLOWED_COLLECTION_TYPES
            ):
                validation_errors.append(
                    f"Invalid collection type: {collection.collection_type}. "
                    f"Must be one of: {HNItemCollection.ALLOWED_COLLECTION_TYPES}"
                )

            # Validate items data based on collection type
            if collection.collection_type == "array":
                validation_errors.extend(self._validate_array_collection(collection))
            elif collection.collection_type == "file_upload":
                validation_errors.extend(
                    self._validate_file_upload_collection(collection)
                )
            elif collection.collection_type == "firebase_pull":
                validation_errors.extend(
                    self._validate_firebase_pull_collection(collection)
                )

            # Validate item counts consistency
            if collection.items and len(collection.items) != collection.total_items:
                collection.total_items = len(collection.items)
                self.logger.info(
                    f"Updated total_items to match actual items count: {collection.total_items}"
                )

            # Set validation results
            if validation_errors:
                error_message = "; ".join(validation_errors)
                collection.add_processing_error(
                    {
                        "type": "validation_error",
                        "message": error_message,
                        "timestamp": collection.created_at,
                    }
                )
                self.logger.warning(
                    f"HNItemCollection {collection.technical_id} validation failed: {error_message}"
                )
            else:
                self.logger.info(
                    f"HNItemCollection {collection.technical_id} validation successful"
                )

            return collection

        except Exception as e:
            self.logger.error(
                f"Error validating HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Add processing error
            if hasattr(entity, "add_processing_error"):
                entity.add_processing_error(
                    {
                        "type": "processing_error",
                        "message": f"Validation processing error: {str(e)}",
                        "timestamp": (
                            entity.created_at if hasattr(entity, "created_at") else None
                        ),
                    }
                )
            raise

    def _validate_array_collection(self, collection: HNItemCollection) -> List[str]:
        """Validate array collection specific requirements."""
        errors = []

        if not collection.items:
            errors.append("Array collection must have items data")
        elif not isinstance(collection.items, list):
            errors.append("Array collection items must be a list")
        else:
            # Validate each item has required HN fields
            for i, item in enumerate(collection.items):
                if not isinstance(item, dict):
                    errors.append(f"Item {i} must be a dictionary")
                    continue

                # Check for required HN API fields
                if "id" not in item:
                    errors.append(f"Item {i} missing required field: id")
                if "type" not in item:
                    errors.append(f"Item {i} missing required field: type")
                elif item["type"] not in ["job", "story", "comment", "poll", "pollopt"]:
                    errors.append(f"Item {i} has invalid type: {item['type']}")

        return errors

    def _validate_file_upload_collection(
        self, collection: HNItemCollection
    ) -> List[str]:
        """Validate file upload collection specific requirements."""
        errors = []

        if not collection.file_name:
            errors.append("File upload collection must have file_name")

        if not collection.file_format:
            errors.append("File upload collection must have file_format")
        elif collection.file_format not in ["json", "csv"]:
            errors.append(f"Unsupported file format: {collection.file_format}")

        if collection.file_size is not None and collection.file_size <= 0:
            errors.append("File size must be positive")

        # If items are already parsed, validate them
        if collection.items:
            errors.extend(self._validate_array_collection(collection))

        return errors

    def _validate_firebase_pull_collection(
        self, collection: HNItemCollection
    ) -> List[str]:
        """Validate Firebase pull collection specific requirements."""
        errors = []

        if not collection.firebase_endpoint:
            errors.append("Firebase pull collection must have firebase_endpoint")

        # Validate Firebase endpoint format
        if (
            collection.firebase_endpoint
            and not collection.firebase_endpoint.startswith("https://")
        ):
            errors.append("Firebase endpoint must be a valid HTTPS URL")

        # Validate filters if present
        if collection.firebase_filters:
            if not isinstance(collection.firebase_filters, dict):
                errors.append("Firebase filters must be a dictionary")

        return errors
