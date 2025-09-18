"""
RestoreCategoryProcessor for Cyoda Client Application

Handles the restoration of Category instances when they are reactivated from archived state.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class RestoreCategoryProcessor(CyodaProcessor):
    """
    Processor for restoring Category entities when they are reactivated from archived state.
    Clears archived date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RestoreCategoryProcessor",
            description="Restores Category instances by clearing archived date and updating timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Restore the Category entity according to functional requirements.

        Args:
            entity: The Category entity to restore
            **kwargs: Additional processing parameters

        Returns:
            The restored category with archived date cleared
        """
        try:
            self.logger.info(
                f"Restoring Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Clear archived date and update timestamp
            category.clear_archived_date()

            self.logger.info(
                f"Category {category.technical_id} restored successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error restoring category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
