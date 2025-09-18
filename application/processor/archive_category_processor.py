"""
ArchiveCategoryProcessor for Cyoda Client Application

Handles the archiving of Category instances when they are deactivated.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class ArchiveCategoryProcessor(CyodaProcessor):
    """
    Processor for archiving Category entities when they are deactivated.
    Sets archived date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ArchiveCategoryProcessor",
            description="Archives Category instances by setting archived date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Archive the Category entity according to functional requirements.

        Args:
            entity: The Category entity to archive
            **kwargs: Additional processing parameters

        Returns:
            The archived category with archived date set
        """
        try:
            self.logger.info(
                f"Archiving Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Set archived date and update timestamp
            category.set_archived_date()

            self.logger.info(
                f"Category {category.technical_id} archived successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error archiving category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
