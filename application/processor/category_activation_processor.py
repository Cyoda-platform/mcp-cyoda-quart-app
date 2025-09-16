"""Category Activation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.category.version_1.category import Category
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CategoryActivationProcessor(CyodaProcessor):
    """Processor for reactivating categories."""

    def __init__(self):
        super().__init__(
            name="CategoryActivationProcessor", description="Reactivates category"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process category activation."""
        try:
            if not isinstance(entity, Category):
                raise ProcessorError(self.name, "Entity must be a Category instance")

            # Validate category is inactive
            if entity.state not in ["inactive"]:
                raise ProcessorError(
                    self.name,
                    f"Category must be inactive for activation, current state: {entity.state}",
                )

            # Set active status and update timestamps
            entity.isActive = True
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add activation metadata
            entity.add_metadata(
                "reactivated_at", datetime.now(timezone.utc).isoformat()
            )
            entity.add_metadata("activation_processed", True)

            # Clear deactivation metadata
            if entity.metadata:
                entity.metadata.pop("deactivated_at", None)

            logger.info(f"Successfully reactivated category {entity.name}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process category activation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process category activation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Category) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Category"
        )
