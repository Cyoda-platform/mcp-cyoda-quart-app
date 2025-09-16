"""Owner Activation Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)


class OwnerActivationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if owner can be reactivated."""
    
    def __init__(self):
        super().__init__(
            name="OwnerActivationCriterion",
            description="Check if owner can be reactivated"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if owner can be reactivated."""
        try:
            if not isinstance(entity, Owner):
                raise CriteriaError(self.name, "Entity must be an Owner instance")
            
            # Check if owner state is INACTIVE
            if entity.state != "inactive":
                logger.debug(f"Owner {entity.entity_id} is not inactive, current state: {entity.state}")
                return False
            
            # TODO: In a real implementation, this would:
            # 1. Check if owner has no outstanding issues
            # 2. Validate account is in good standing
            # 3. Check for any pending violations or restrictions
            
            # Check if owner has outstanding issues (from metadata)
            outstanding_issues = entity.get_metadata("outstanding_issues", False)
            if outstanding_issues:
                logger.debug(f"Owner {entity.entity_id} has outstanding issues")
                return False
            
            # Check if account is in good standing (from metadata)
            good_standing = entity.get_metadata("good_standing", True)
            if not good_standing:
                logger.debug(f"Owner {entity.entity_id} account is not in good standing")
                return False
            
            # Check if there are any restrictions (from metadata)
            restrictions = entity.get_metadata("restrictions", [])
            if restrictions:
                logger.debug(f"Owner {entity.entity_id} has active restrictions: {restrictions}")
                return False
            
            logger.debug(f"Owner {entity.entity_id} can be reactivated")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check activation criteria for owner {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check owner activation: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Owner"
        )
