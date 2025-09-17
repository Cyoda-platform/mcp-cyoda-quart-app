"""
ValidateHNItemProcessor for Cyoda Client Application

Validates HN item structure and data integrity as specified in workflow requirements.
"""

import logging
from typing import Any

from application.entity.hnitem.version_1.hnitem import HNItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ValidateHNItemProcessor(CyodaProcessor):
    """
    Processor for validating HNItem structure and data integrity.

    Validates required fields, data types, and ensures HN API compliance.
    """

    def __init__(self) -> None:
        super().__init__(
            name="validate_hn_item",
            description="Validates HN item structure and data integrity",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Validate the HNItem according to functional requirements.

        Args:
            entity: The HNItem to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated entity with validation status
        """
        try:
            self.logger.info(
                f"Validating HNItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Perform validation checks
            validation_errors = []

            # Validate required fields based on item type
            if hn_item.type == "story":
                if not hn_item.title and not hn_item.url:
                    validation_errors.append("Stories must have either title or URL")
                if hn_item.score is None:
                    validation_errors.append("Stories must have a score")

            elif hn_item.type == "comment":
                if not hn_item.text:
                    validation_errors.append("Comments must have text content")
                if hn_item.parent is None:
                    validation_errors.append("Comments must have a parent ID")

            elif hn_item.type == "job":
                if not hn_item.title:
                    validation_errors.append("Job postings must have a title")

            elif hn_item.type == "poll":
                if not hn_item.title:
                    validation_errors.append("Polls must have a title")
                if not hn_item.parts:
                    validation_errors.append("Polls must have poll options (parts)")

            elif hn_item.type == "pollopt":
                if not hn_item.text:
                    validation_errors.append("Poll options must have text")
                if hn_item.poll is None:
                    validation_errors.append("Poll options must reference a poll ID")

            # Validate author field
            if hn_item.by and len(hn_item.by.strip()) == 0:
                validation_errors.append("Author field cannot be empty string")

            # Validate URL format if present
            if hn_item.url:
                if not (
                    hn_item.url.startswith("http://")
                    or hn_item.url.startswith("https://")
                ):
                    validation_errors.append("URL must start with http:// or https://")

            # Validate relationships
            if hn_item.kids:
                for kid_id in hn_item.kids:
                    if not isinstance(kid_id, int) or kid_id <= 0:
                        validation_errors.append(f"Invalid child ID: {kid_id}")

            if hn_item.parts:
                for part_id in hn_item.parts:
                    if not isinstance(part_id, int) or part_id <= 0:
                        validation_errors.append(f"Invalid part ID: {part_id}")

            # Set validation status
            if validation_errors:
                validation_status = "FAILED"
                self.logger.warning(
                    f"HNItem {hn_item.technical_id} validation failed: {validation_errors}"
                )
            else:
                validation_status = "PASSED"
                self.logger.info(f"HNItem {hn_item.technical_id} validation passed")

            # Update validation status
            hn_item.update_validation_status(validation_status)

            # Add validation details to metadata
            if not hn_item.metadata:
                hn_item.metadata = {}
            hn_item.metadata["validation_errors"] = validation_errors
            hn_item.metadata["validation_timestamp"] = hn_item.updated_at

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error validating HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
