"""
Owner Registration Processor for Purrfect Pets API.

Handles the registration of new pet owners.
"""
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class OwnerRegistrationProcessor(CyodaProcessor):
    """Processor to register a new pet owner."""
    
    def __init__(self, name: str = "OwnerRegistrationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Register a new pet owner"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner registration."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, f"Expected Owner entity, got {type(entity)}")
            
            owner = entity
            
            # Validate required fields
            self._validate_required_fields(owner)
            
            # Validate email format
            self._validate_email_format(owner.email)
            
            # Check for duplicate email
            await self._check_duplicate_email(owner.email)
            
            # Set registration date if not already set
            if not owner.registration_date:
                owner.registration_date = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            # Generate unique owner_id if not provided
            if not owner.owner_id:
                owner.owner_id = f"OWN-{owner.entity_id[:8].upper()}"
            
            # Log registration event
            owner.add_metadata("registration_processor", self.name)
            owner.add_metadata("registration_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully registered owner {owner.owner_id} with email {owner.email}")
            
            return owner
            
        except Exception as e:
            logger.exception(f"Failed to register owner {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to register owner: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner)
    
    def _validate_required_fields(self, owner: Owner) -> None:
        """Validate that all required fields are present."""
        if not owner.first_name or not owner.first_name.strip():
            raise ValueError("First name is required")
        
        if not owner.last_name or not owner.last_name.strip():
            raise ValueError("Last name is required")
        
        if not owner.email or not owner.email.strip():
            raise ValueError("Email is required")
        
        if not owner.phone or not owner.phone.strip():
            raise ValueError("Phone number is required")
    
    def _validate_email_format(self, email: str) -> None:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
    
    async def _check_duplicate_email(self, email: str) -> None:
        """Check for duplicate email addresses."""
        # Mock implementation - in reality, this would query the entity service
        logger.debug(f"Checking for duplicate email: {email}")
        
        # TODO: Implement actual duplicate check
        # entity_service = self._get_entity_service()
        # existing_owners = await entity_service.search("Owner", {"email": email})
        # if existing_owners:
        #     raise ValueError(f"Email {email} is already registered")
    
    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service
        return get_entity_service()
