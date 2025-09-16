"""
Owner Contact Validation Criterion for Purrfect Pets API.

Validates that owner's contact information is correct and verified.
"""
import logging
import re
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class OwnerContactValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate owner's contact information."""
    
    def __init__(self, name: str = "OwnerContactValidationCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Validate that owner's contact information is correct and verified"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the owner meets contact validation criteria."""
        try:
            if not isinstance(entity, Owner):
                logger.warning(f"Expected Owner entity, got {type(entity)}")
                return False
            
            owner = entity
            
            # Email format validation
            if not self._validate_email_format(owner.email):
                logger.info(f"Email format validation failed for owner {owner.owner_id}")
                return False
            
            # Email deliverability check
            if not await self._check_email_deliverable(owner.email):
                logger.info(f"Email deliverability check failed for owner {owner.owner_id}")
                return False
            
            # Phone number format validation
            if not self._validate_phone_format(owner.phone):
                logger.info(f"Phone format validation failed for owner {owner.owner_id}")
                return False
            
            # At least one contact method verified
            if not await self._check_contact_verification(owner):
                logger.info(f"Contact verification check failed for owner {owner.owner_id}")
                return False
            
            # Emergency contact validation
            if not self._validate_emergency_contact(owner):
                logger.info(f"Emergency contact validation failed for owner {owner.owner_id}")
                return False
            
            # Address information validation
            if not self._validate_address_information(owner):
                logger.info(f"Address validation failed for owner {owner.owner_id}")
                return False
            
            logger.info(f"All contact validations passed for owner {owner.owner_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check owner contact validation criteria for entity {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check owner contact validation criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Owner)
    
    def _validate_email_format(self, email: str) -> bool:
        """Validate email format."""
        if not email or not email.strip():
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email.strip()))
    
    async def _check_email_deliverable(self, email: str) -> bool:
        """Check if email is deliverable."""
        # TODO: Implement actual email deliverability check
        # This would typically involve DNS MX record checks, SMTP validation, etc.
        logger.debug(f"Mock validation: Email {email} is deliverable")
        return True
    
    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone number format for the region."""
        if not phone or not phone.strip():
            return False
        
        # Remove common formatting characters
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation - at least 10 digits
        if len(cleaned_phone) < 10:
            return False
        
        # TODO: Implement region-specific phone validation
        return True
    
    async def _check_contact_verification(self, owner: Owner) -> bool:
        """Check that at least one contact method is verified."""
        # Check metadata for verification status
        email_verified = owner.get_metadata("email_verified", False)
        phone_verified = owner.get_metadata("phone_verified", False)
        
        if email_verified or phone_verified:
            return True
        
        # TODO: Implement actual verification check
        # For now, assume verification is in progress if verification tokens exist
        verification_tokens = owner.get_metadata("verification_tokens")
        if verification_tokens:
            logger.debug(f"Verification tokens found for owner {owner.owner_id}")
            return True
        
        return False
    
    def _validate_emergency_contact(self, owner: Owner) -> bool:
        """Validate emergency contact information if required."""
        # Emergency contact is optional but if provided, should be valid
        if owner.emergency_contact_name and not owner.emergency_contact_phone:
            return False
        
        if owner.emergency_contact_phone and not owner.emergency_contact_name:
            return False
        
        # If emergency contact phone is provided, validate format
        if owner.emergency_contact_phone:
            cleaned_phone = re.sub(r'[^\d+]', '', owner.emergency_contact_phone)
            if len(cleaned_phone) < 10:
                return False
        
        return True
    
    def _validate_address_information(self, owner: Owner) -> bool:
        """Validate address information is complete if provided."""
        # Address is optional, but if city is provided, postal code should be too
        if owner.city and not owner.postal_code:
            return False
        
        if owner.postal_code and not owner.city:
            return False
        
        # Basic postal code format validation
        if owner.postal_code:
            # Allow various postal code formats (US ZIP, Canadian, etc.)
            postal_pattern = r'^[A-Za-z0-9\s\-]{3,10}$'
            if not re.match(postal_pattern, owner.postal_code):
                return False
        
        return True
