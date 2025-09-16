"""
Active Subscriber Criterion for checking if subscriber is active and can receive emails.
"""
import logging
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class ActiveSubscriberCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if subscriber is active and can receive emails."""
    
    def __init__(self, name: str = "ActiveSubscriberCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Checks if subscriber is active and can receive emails"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if subscriber is active."""
        try:
            if not isinstance(entity, Subscriber):
                return False
            
            # Check if subscriber is active
            if not entity.isActive:
                return False
            
            # Check entity state
            if entity.state == "bounced":
                return False
            
            if entity.state == "unsubscribed":
                return False
            
            # Additional checks for inactive states
            inactive_states = ["pending", "initial_state"]
            if entity.state in inactive_states:
                return False
            
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check active criteria for subscriber {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check active criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Subscriber)
