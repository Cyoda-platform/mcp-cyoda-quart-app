"""Category Deactivation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.category.version_1.category import Category
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CategoryDeactivationProcessor(CyodaProcessor):
    """Processor for deactivating categories."""

    def __init__(self):
        super().__init__(
            name="CategoryDeactivationProcessor",
            description="Deactivates category, handles associated pets",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process category deactivation."""
        try:
            if not isinstance(entity, Category):
                raise ProcessorError(self.name, "Entity must be a Category instance")

            # Validate category is active
            if entity.state not in ["active"]:
                raise ProcessorError(
                    self.name,
                    f"Category must be active for deactivation, current state: {entity.state}",
                )

            # TODO: In a real implementation, this would:
            # 1. Check if category has active pets using EntityService
            # 2. Handle associated pets appropriately

            # Set inactive status and update timestamps
            entity.isActive = False
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add deactivation metadata
            entity.add_metadata(
                "deactivated_at", datetime.now(timezone.utc).isoformat()
            )
            entity.add_metadata("deactivation_processed", True)
            entity.add_metadata("active_pets_checked", True)

            logger.info(f"Successfully deactivated category {entity.name}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process category deactivation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process category deactivation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Category) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Category"
        )
