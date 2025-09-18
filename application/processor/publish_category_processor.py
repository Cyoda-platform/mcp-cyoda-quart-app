"""
PublishCategoryProcessor for Cyoda Client Application

Handles the publishing of Category instances when they are activated.
"""

import logging
from typing import Any

from application.entity.category.version_1.category import Category
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PublishCategoryProcessor(CyodaProcessor):
    """
    Processor for publishing Category entities when they are activated.
    Sets published date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PublishCategoryProcessor",
            description="Publishes Category instances by setting published date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Publish the Category entity according to functional requirements.

        Args:
            entity: The Category entity to publish
            **kwargs: Additional processing parameters

        Returns:
            The published category with published date set
        """
        try:
            self.logger.info(
                f"Publishing Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Set published date and update timestamp
            category.set_published_date()

            self.logger.info(f"Category {category.technical_id} published successfully")

            return category

        except Exception as e:
            self.logger.error(
                f"Error publishing category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
