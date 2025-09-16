"""Owner Verification Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)


class OwnerVerificationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if owner can be verified."""
    
    def __init__(self):
        super().__init__(
            name="OwnerVerificationCriterion",
            description="Check if owner can be verified"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if owner can be verified."""
        try:
            if not isinstance(entity, Owner):
                raise CriteriaError(self.name, "Entity must be an Owner instance")
            
            # Check if owner state is PENDING_VERIFICATION
            if entity.state != "pending_verification":
                logger.debug(f"Owner {entity.entity_id} is not pending verification, current state: {entity.state}")
                return False
            
            # Get verification token from kwargs
            verification_token = kwargs.get("verificationToken") or kwargs.get("verification_token")
            
            if not verification_token:
                logger.debug(f"No verification token provided for owner {entity.entity_id}")
                return False
            
            # Check if verification token is valid (simplified validation)
            stored_token = entity.get_metadata("verification_token")
            if not stored_token:
                logger.debug(f"No stored verification token found for owner {entity.entity_id}")
                return False
            
            if stored_token != verification_token:
                logger.debug(f"Verification token mismatch for owner {entity.entity_id}")
                return False
            
            # TODO: In a real implementation, this would:
            # 1. Check if token is not expired
            # 2. Validate email is verified
            
            # Check if email is verified (from metadata)
            email_verified = entity.get_metadata("email_verified", False)
            if email_verified:
                logger.debug(f"Owner {entity.entity_id} email is already verified")
                return True
            
            logger.debug(f"Owner {entity.entity_id} can be verified")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check verification criteria for owner {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check owner verification: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Owner"
        )
