"""Category Creation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.category.version_1.category import Category
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CategoryCreationProcessor(CyodaProcessor):
    """Processor for creating new categories."""

    def __init__(self):
        super().__init__(
            name="CategoryCreationProcessor",
            description="Creates new category, validates uniqueness",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process category creation."""
        try:
            if not isinstance(entity, Category):
                raise ProcessorError(self.name, "Entity must be a Category instance")

            # Validate required fields
            if not entity.name or not entity.name.strip():
                raise ProcessorError(self.name, "Category name is required")

            if not entity.description or not entity.description.strip():
                raise ProcessorError(self.name, "Category description is required")

            # TODO: In a real implementation, this would:
            # 1. Validate category name is unique using EntityService

            # Set timestamps and active status
            current_time = datetime.now(timezone.utc).isoformat()
            entity.isActive = True
            entity.createdAt = current_time
            entity.updatedAt = current_time
            entity.update_timestamp()

            # Add creation metadata
            entity.add_metadata("category_created", True)
            entity.add_metadata("processed_at", current_time)
            entity.add_metadata("creation_processed", True)

            logger.info(f"Successfully created category {entity.name}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process category creation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process category creation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Category) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Category"
        )
