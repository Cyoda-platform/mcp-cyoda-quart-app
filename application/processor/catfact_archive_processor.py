"""
CatFact Archive Processor for archiving cat facts after distribution.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.catfact.version_1.catfact import CatFact
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class CatFactArchiveProcessor(CyodaProcessor):
    """Processor to archive cat facts after distribution."""
    
    def __init__(self, name: str = "CatFactArchiveProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Archives cat fact after distribution"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Archive cat fact after distribution."""
        try:
            if not isinstance(entity, CatFact):
                raise ProcessorError(self.name, f"Expected CatFact entity, got {type(entity)}")
            
            # Validate cat fact has been sent
            if entity.state != "sent":
                raise ProcessorError(self.name, f"CatFact must be in sent state to archive, current state: {entity.state}")
            
            # Add archival metadata
            entity.add_metadata("archived_at", entity.updated_at)
            entity.add_metadata("archival_reason", "Automatic archival after distribution")
            
            logger.info(f"Archived cat fact: {entity.fact[:50]}...")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to archive cat fact {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to archive cat fact: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, CatFact)
