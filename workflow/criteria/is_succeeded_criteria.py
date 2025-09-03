"""
Is Succeeded Criteria checker for job success validation.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from entity.job import JobEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class IsSucceededCriteria(CyodaCriteriaChecker):
    """Criteria checker to determine if a job has succeeded."""
    
    def __init__(self, name: str = "is_succeeded", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if a job entity has succeeded"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the job has succeeded."""
        try:
            # Check entity state
            if entity.state == "SUCCEEDED":
                return True
            
            # Check metadata for legacy compatibility
            status = entity.get_metadata("status")
            state = entity.get_metadata("state")
            
            return status == "SUCCEEDED" or state == "SUCCEEDED"
            
        except Exception as e:
            logger.exception(f"Failed to check success criteria for entity {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check success criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, JobEntity) or entity.get_metadata("entity_type") == "job"
