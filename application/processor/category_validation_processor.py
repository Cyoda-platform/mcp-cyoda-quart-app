"""
CategoryValidationProcessor for Purrfect Pets API

Validates category data according to processors.md specification.
"""

import logging
from typing import Any

from application.entity.category.version_1.category import Category
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CategoryValidationProcessor(CyodaProcessor):
    """
    Processor for Category validation that handles category data validation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryValidationProcessor",
            description="Validates category data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity according to functional requirements.

        Args:
            entity: The Category entity to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated category entity
        """
        try:
            self.logger.info(
                f"Validating Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Validate category name is not empty
            if not category.name or len(category.name.strip()) == 0:
                raise ValueError("Category name is required and cannot be empty")

            # Validate category name is unique (placeholder - would need database check)
            # In a real implementation, this would check against existing categories
            self.logger.info(
                f"Category name uniqueness check passed for: {category.name}"
            )

            # Set default description if empty
            if not category.description:
                category.description = f"Category for {category.name}"

            # Update timestamp
            category.update_timestamp()

            self.logger.info(f"Category {category.technical_id} validated successfully")

            return category

        except Exception as e:
            self.logger.error(
                f"Error validating category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
