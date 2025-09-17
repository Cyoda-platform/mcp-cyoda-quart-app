"""
ValidateItemStructure Processor for HNItem

Validates that an HNItem meets Firebase HN API format requirements
before it can proceed to the enrichment stage.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitem.version_1.hnitem import HNItem


class ValidateItemStructure(CyodaProcessor):
    """
    Processor for validating HNItem structure according to Firebase HN API format.
    Validates required fields and item type constraints.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validate_item_structure",
            description="Validates HNItem structure according to Firebase HN API format",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Validate the HNItem structure according to Firebase HN API requirements.

        Args:
            entity: The HNItem to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated entity with validation status
        """
        try:
            self.logger.info(
                f"Validating HNItem structure {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Validate required fields
            validation_errors = []

            # Check for required fields
            if hn_item.id is None:
                validation_errors.append("Missing required field: id")

            if not hn_item.type:
                validation_errors.append("Missing required field: type")
            elif hn_item.type not in HNItem.ALLOWED_TYPES:
                validation_errors.append(
                    f"Invalid type: {hn_item.type}. Must be one of: {HNItem.ALLOWED_TYPES}"
                )

            # Type-specific validations
            if hn_item.type == "story":
                if not hn_item.title and not hn_item.text:
                    validation_errors.append("Stories must have either title or text")

            elif hn_item.type == "comment":
                if not hn_item.text:
                    validation_errors.append("Comments must have text")
                if hn_item.parent is None:
                    validation_errors.append("Comments must have a parent")

            elif hn_item.type == "job":
                if not hn_item.title:
                    validation_errors.append("Jobs must have a title")

            elif hn_item.type == "poll":
                if not hn_item.title:
                    validation_errors.append("Polls must have a title")
                if not hn_item.parts:
                    validation_errors.append("Polls must have parts (poll options)")

            elif hn_item.type == "pollopt":
                if hn_item.poll is None:
                    validation_errors.append("Poll options must reference a poll")

            # Validate data consistency
            if hn_item.kids and not isinstance(hn_item.kids, list):
                validation_errors.append("Kids field must be a list of integers")

            if hn_item.parts and not isinstance(hn_item.parts, list):
                validation_errors.append("Parts field must be a list of integers")

            # Set validation results
            if validation_errors:
                hn_item.validation_error = "; ".join(validation_errors)
                hn_item.validation_status = "invalid"
                self.logger.warning(
                    f"HNItem {hn_item.technical_id} validation failed: {hn_item.validation_error}"
                )
            else:
                hn_item.validation_error = None
                hn_item.validation_status = "valid"
                self.logger.info(f"HNItem {hn_item.technical_id} validation successful")

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error validating HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Set validation error on the entity
            if hasattr(entity, "validation_error"):
                entity.validation_error = f"Validation processing error: {str(e)}"
                entity.validation_status = "error"
            raise
