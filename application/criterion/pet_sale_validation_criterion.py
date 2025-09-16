"""Pet Sale Validation Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.pet.version_1.pet import Pet

logger = logging.getLogger(__name__)


class PetSaleValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate pet can be sold."""
    
    def __init__(self):
        super().__init__(
            name="PetSaleValidationCriterion",
            description="Check pet is pending and owner is verified"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if pet can be sold."""
        try:
            if not isinstance(entity, Pet):
                raise CriteriaError(self.name, "Entity must be a Pet instance")
            
            # Check if pet state is PENDING
            if entity.state != "pending":
                logger.debug(f"Pet {entity.entity_id} is not pending, current state: {entity.state}")
                return False
            
            # Check if pet has an owner
            if not entity.ownerId:
                logger.debug(f"Pet {entity.entity_id} has no owner assigned")
                return False
            
            # Get owner information from kwargs
            owner = kwargs.get("owner")
            owner_id = kwargs.get("owner_id") or kwargs.get("ownerId")
            
            # If owner entity is provided, validate it
            if owner:
                # Check if owner state is ACTIVE
                if hasattr(owner, 'state') and owner.state != "active":
                    logger.debug(f"Owner {owner.entity_id} is not active, current state: {owner.state}")
                    return False
                
                # Check if pet's owner matches the provided owner
                if hasattr(owner, 'id') and entity.ownerId != owner.id:
                    logger.debug(f"Pet owner {entity.ownerId} does not match provided owner {owner.id}")
                    return False
            
            # If only owner_id is provided, check it matches
            elif owner_id and entity.ownerId != owner_id:
                logger.debug(f"Pet owner {entity.ownerId} does not match provided owner_id {owner_id}")
                return False
            
            # TODO: In a real implementation, this would:
            # 1. Fetch owner entity using EntityService
            # 2. Validate owner state is ACTIVE
            
            logger.debug(f"Pet {entity.entity_id} can be sold to owner {entity.ownerId}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check sale validation criteria for pet {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check pet sale validation: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Pet"
        )
