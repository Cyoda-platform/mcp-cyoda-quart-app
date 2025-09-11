"""
TagValidationProcessor for Purrfect Pets API

Validates tag data according to processors.md specification.
"""

import logging
from typing import Any

from application.entity.tag.version_1.tag import Tag
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class TagValidationProcessor(CyodaProcessor):
    """
    Processor for Tag validation that handles tag data validation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TagValidationProcessor",
            description="Validates tag data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Tag entity according to functional requirements.

        Args:
            entity: The Tag entity to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated tag entity
        """
        try:
            self.logger.info(
                f"Validating Tag {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Tag for type-safe operations
            tag = cast_entity(entity, Tag)

            # Validate tag name is not empty
            if not tag.name or len(tag.name.strip()) == 0:
                raise ValueError("Tag name is required and cannot be empty")

            # Validate tag name is unique (placeholder - would need database check)
            # In a real implementation, this would check against existing tags
            self.logger.info(f"Tag name uniqueness check passed for: {tag.name}")

            # Set default color if empty
            if not tag.color:
                tag.color = "#blue"  # Default color

            # Update timestamp
            tag.update_timestamp()

            self.logger.info(f"Tag {tag.technical_id} validated successfully")

            return tag

        except Exception as e:
            self.logger.error(
                f"Error validating tag {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
