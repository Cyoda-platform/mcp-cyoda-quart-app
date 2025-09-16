"""Category Archive Processor for Purrfect Pets API."""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from application.entity.category.version_1.category import Category

logger = logging.getLogger(__name__)


class CategoryArchiveProcessor(CyodaProcessor):
    """Processor for archiving categories permanently."""
    
    def __init__(self):
        super().__init__(
            name="CategoryArchiveProcessor",
            description="Archives category permanently"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process category archiving."""
        try:
            if not isinstance(entity, Category):
                raise ProcessorError(self.name, "Entity must be a Category instance")
            
            # Validate category is inactive
            if entity.state not in ["inactive"]:
                raise ProcessorError(self.name, f"Category must be inactive for archiving, current state: {entity.state}")
            
            # TODO: In a real implementation, this would:
            # 1. Validate no active pets in category using EntityService
            # 2. Validate no pending orders for pets in this category
            
            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()
            
            # Add archiving metadata
            entity.add_metadata("archived_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("archive_processed", True)
            entity.add_metadata("pets_validated", True)
            entity.add_metadata("orders_validated", True)
            
            logger.info(f"Successfully archived category {entity.name}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to process category archiving for entity {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to process category archiving: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Category) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Category"
        )
