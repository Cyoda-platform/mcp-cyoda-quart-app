"""
CategoryReactivationProcessor for Purrfect Pets Application

Reactivates an inactive category as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class CategoryReactivationProcessor(CyodaProcessor):
    """
    Processor for reactivating Category entities from inactive status.
    Validates category information is still relevant.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryReactivationProcessor",
            description="Reactivate an inactive category"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity for reactivation.

        Args:
            entity: The Category entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated Category entity
        """
        try:
            self.logger.info(
                f"Processing Category reactivation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Validate category information is still relevant
            if not category.name or len(category.name.strip()) == 0:
                raise ValueError("Category name is required for reactivation")

            # Update category information if provided in kwargs
            update_data = kwargs.get('update_data', {})
            if update_data:
                if 'description' in update_data:
                    category.description = update_data['description']
                if 'imageUrl' in update_data or 'image_url' in update_data:
                    category.image_url = update_data.get('imageUrl') or update_data.get('image_url')

            # Set updated timestamp
            category.update_timestamp()

            self.logger.info(f"Category reactivation processed successfully for {category.technical_id}")
            return category

        except Exception as e:
            self.logger.error(
                f"Error processing Category reactivation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
