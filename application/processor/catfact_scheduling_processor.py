"""
CatFact Scheduling Processor for scheduling cat facts for weekly distribution.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.catfact.version_1.catfact import CatFact
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class CatFactSchedulingProcessor(CyodaProcessor):
    """Processor to schedule cat facts for weekly distribution."""
    
    def __init__(self, name: str = "CatFactSchedulingProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Schedules cat fact for weekly distribution"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Schedule cat fact for distribution."""
        try:
            if not isinstance(entity, CatFact):
                raise ProcessorError(self.name, f"Expected CatFact entity, got {type(entity)}")
            
            # Validate cat fact has content
            if not entity.fact:
                raise ProcessorError(self.name, "CatFact must have fact content to be scheduled")
            
            # Calculate next weekly send date (next Monday at 9 AM)
            now = datetime.now(timezone.utc)
            
            # Find next Monday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:  # If today is Monday
                days_until_monday = 7  # Schedule for next Monday
            
            next_monday = now + timedelta(days=days_until_monday)
            scheduled_date = next_monday.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # Set scheduled send date
            entity.scheduledSendDate = scheduled_date
            
            logger.info(f"Scheduled cat fact for {scheduled_date}: {entity.fact[:50]}...")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to schedule cat fact {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to schedule cat fact: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, CatFact)
