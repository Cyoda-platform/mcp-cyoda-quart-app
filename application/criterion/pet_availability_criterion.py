"""Pet Availability Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.pet.version_1.pet import Pet

logger = logging.getLogger(__name__)


class PetAvailabilityCriterion(CyodaCriteriaChecker):
    """Criteria checker to verify if pet is available for reservation or sale."""
    
    def __init__(self):
        super().__init__(
            name="PetAvailabilityCriterion",
            description="Check if pet is available for reservation or sale"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if pet is available."""
        try:
            if not isinstance(entity, Pet):
                raise CriteriaError(self.name, "Entity must be a Pet instance")
            
            # Check if pet state is AVAILABLE
            if entity.state != "available":
                logger.debug(f"Pet {entity.entity_id} is not available, current state: {entity.state}")
                return False
            
            # Check if pet is not already reserved (ownerId should be null)
            if entity.ownerId is not None:
                logger.debug(f"Pet {entity.entity_id} is already reserved by owner {entity.ownerId}")
                return False
            
            logger.debug(f"Pet {entity.entity_id} is available for reservation/sale")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check availability criteria for pet {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check pet availability: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Pet"
        )
