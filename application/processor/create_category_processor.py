"""
CreateCategoryProcessor for Cyoda Client Application

Handles the creation of Category instances when they are first created.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class CreateCategoryProcessor(CyodaProcessor):
    """
    Processor for creating Category entities when they are first created.
    Sets created date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateCategoryProcessor",
            description="Creates Category instances with created date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Create the Category entity according to functional requirements.

        Args:
            entity: The Category entity to create
            **kwargs: Additional processing parameters

        Returns:
            The created category with created date set
        """
        try:
            self.logger.info(
                f"Creating Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Set created date and update timestamp
            category.set_created_date()

            self.logger.info(
                f"Category {category.technical_id} created successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error creating category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
