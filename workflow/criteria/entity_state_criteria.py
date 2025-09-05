"""
Entity State Criteria checker for entity state validation.
"""
import logging
from typing import Any, Dict, Optional, List

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class EntityStateCriteria(CyodaCriteriaChecker):
    """Criteria checker to check if entity is in a specific state."""
    
    def __init__(self, name: str = "entity_state", description: str = "", expected_states: Optional[List[str]] = None):
        super().__init__(
            name=name,
            description=description or f"Checks if entity is in one of the expected states: {expected_states}"
        )
        self.expected_states = expected_states or []
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if entity is in expected state."""
        try:
            # Get expected states from kwargs if not set in constructor
            expected_states = kwargs.get("expected_states", self.expected_states)
            if not expected_states:
                raise CriteriaError(self.name, "No expected states provided")
            
            # Check entity state
            current_state = entity.state
            if current_state in expected_states:
                return True
            
            # Check metadata for legacy compatibility
            status = entity.get_metadata("status")
            state = entity.get_metadata("state")
            
            return status in expected_states or state in expected_states
            
        except Exception as e:
            if isinstance(e, CriteriaError):
                raise
            logger.exception(f"Failed to check entity state criteria for entity {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check entity state criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return True  # Can check any entity type
