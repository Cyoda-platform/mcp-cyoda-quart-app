"""
Veterinarian Entity for Purrfect Pets API.

Represents a veterinarian who can provide medical care to pets.
"""
import re
from datetime import datetime, timezone
from typing import ClassVar, Optional
from pydantic import Field, validator

from entity.cyoda_entity import CyodaEntity


class Veterinarian(CyodaEntity):
    """
    Veterinarian entity representing a veterinarian in the Purrfect Pets system.
    
    Attributes:
        vet_id: Unique identifier for the veterinarian
        first_name: Veterinarian's first name (max 50 characters)
        last_name: Veterinarian's last name (max 50 characters)
        email: Professional email address
        phone: Professional phone number
        license_number: Veterinary license number
        specialization: Area of specialization
        years_experience: Years of veterinary experience
        hire_date: When the vet was hired
        is_available: Whether the vet is currently available
        working_hours: Typical working schedule
    """
    
    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Veterinarian"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Required fields
    vet_id: str = Field(..., description="Unique identifier for the veterinarian")
    first_name: str = Field(..., max_length=50, description="Veterinarian's first name")
    last_name: str = Field(..., max_length=50, description="Veterinarian's last name")
    email: str = Field(..., description="Professional email address")
    phone: str = Field(..., description="Professional phone number")
    license_number: str = Field(..., description="Veterinary license number")
    hire_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        description="When the vet was hired"
    )
    is_available: bool = Field(default=False, description="Whether the vet is currently available")
    
    # Optional fields
    specialization: Optional[str] = Field(None, description="Area of specialization")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of veterinary experience")
    working_hours: Optional[str] = Field(None, description="Typical working schedule")
    
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
    
    @validator('license_number')
    def validate_license_number(cls, v):
        """Validate license number."""
        if not v or not v.strip():
            raise ValueError("License number cannot be empty")
        return v.strip().upper()
    
    @validator('years_experience')
    def validate_years_experience(cls, v):
        """Validate years of experience."""
        if v is not None and v < 0:
            raise ValueError("Years of experience cannot be negative")
        return v
    
    @validator('specialization')
    def validate_specialization(cls, v):
        """Validate specialization."""
        if v is not None:
            common_specializations = {
                'general practice', 'surgery', 'internal medicine', 'dermatology',
                'cardiology', 'oncology', 'orthopedics', 'ophthalmology',
                'dentistry', 'emergency medicine', 'exotic animals', 'behavior'
            }
            if v.lower() not in common_specializations:
                # Allow custom specializations but log a warning
                pass
            return v.lower()
        return v
    
    def get_full_name(self) -> str:
        """Get the veterinarian's full name."""
        return f"Dr. {self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        """String representation of the veterinarian."""
        return f"Veterinarian(vet_id={self.vet_id}, name={self.get_full_name()}, license={self.license_number})"
