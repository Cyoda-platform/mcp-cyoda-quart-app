"""
WeeklySchedule Fact Retrieval Processor for retrieving cat facts for weekly distribution.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class WeeklyScheduleFactRetrievalProcessor(CyodaProcessor):
    """Processor to retrieve cat facts for weekly distribution."""
    
    def __init__(self, name: str = "WeeklyScheduleFactRetrievalProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Retrieves cat fact for weekly distribution"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Retrieve cat fact for weekly distribution."""
        try:
            if not isinstance(entity, WeeklySchedule):
                raise ProcessorError(self.name, f"Expected WeeklySchedule entity, got {type(entity)}")
            
            # Get entity service
            entity_service = self._get_entity_service()
            
            # Create new CatFact entity
            catfact_data = {
                "fact": ""  # Will be populated by CatFactRetrievalProcessor
            }
            
            # Save CatFact entity (this will trigger its workflow)
            catfact_response = await entity_service.save(catfact_data, "catfact", "1")
            catfact_id = catfact_response.get_id()
            
            # Wait for CatFact to be retrieved and scheduled
            # In a real implementation, this would be handled by the workflow engine
            # For now, we'll just set the catFactId
            entity.catFactId = int(catfact_id) if catfact_id else None
            
            logger.info(f"Retrieved cat fact {catfact_id} for weekly schedule {entity.id}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to retrieve cat fact for weekly schedule {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to retrieve cat fact for weekly schedule: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, WeeklySchedule)
    
    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service
        return get_entity_service()
