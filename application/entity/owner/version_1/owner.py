"""
Owner Entity for Purrfect Pets API.

Represents a pet owner with contact information and preferences.
"""
import re
from datetime import datetime, timezone
from typing import ClassVar, Optional
from pydantic import Field, validator

from entity.cyoda_entity import CyodaEntity


class Owner(CyodaEntity):
    """
    Owner entity representing a pet owner in the Purrfect Pets system.
    
    Attributes:
        owner_id: Unique identifier for the owner
        first_name: Owner's first name (max 50 characters)
        last_name: Owner's last name (max 50 characters)
        email: Email address (must be valid email format)
        phone: Primary phone number
        address: Home address
        city: City of residence
        postal_code: Postal/ZIP code
        emergency_contact_name: Emergency contact person
        emergency_contact_phone: Emergency contact phone
        registration_date: When the owner registered
        preferred_vet_id: Reference to preferred veterinarian
        communication_preferences: Email/SMS/Phone preferences
    """
    
    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Owner"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Required fields
    owner_id: str = Field(..., description="Unique identifier for the owner")
    first_name: str = Field(..., max_length=50, description="Owner's first name")
    last_name: str = Field(..., max_length=50, description="Owner's last name")
    email: str = Field(..., description="Email address (must be valid email format)")
    phone: str = Field(..., description="Primary phone number")
    registration_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        description="When the owner registered"
    )
    
    # Optional fields
    address: Optional[str] = Field(None, description="Home address")
    city: Optional[str] = Field(None, description="City of residence")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact person")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    preferred_vet_id: Optional[str] = Field(None, description="Reference to preferred veterinarian")
    communication_preferences: Optional[str] = Field(None, description="Email/SMS/Phone preferences")
    
    @validator('first_name')
    def validate_first_name(cls, v):
        """Validate first name."""
        if not v or not v.strip():
            raise ValueError("First name cannot be empty")
        if len(v.strip()) > 50:
            raise ValueError("First name cannot exceed 50 characters")
        return v.strip()
    
    @validator('last_name')
    def validate_last_name(cls, v):
        """Validate last name."""
        if not v or not v.strip():
            raise ValueError("Last name cannot be empty")
        if len(v.strip()) > 50:
            raise ValueError("Last name cannot exceed 50 characters")
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Invalid email format")
        return v.strip().lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        if not v or not v.strip():
            raise ValueError("Phone number cannot be empty")
        
        # Remove common phone number formatting
        cleaned_phone = re.sub(r'[^\d+]', '', v)
        if len(cleaned_phone) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v.strip()
    
    @validator('communication_preferences')
    def validate_communication_preferences(cls, v):
        """Validate communication preferences."""
        if v is not None:
            allowed_prefs = {'email', 'sms', 'phone', 'email,sms', 'email,phone', 'sms,phone', 'email,sms,phone'}
            if v.lower() not in allowed_prefs:
                raise ValueError(f"Communication preferences must be one of: {', '.join(allowed_prefs)}")
            return v.lower()
        return v
    
    def get_full_name(self) -> str:
        """Get the owner's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        """String representation of the owner."""
        return f"Owner(owner_id={self.owner_id}, name={self.get_full_name()}, email={self.email})"
