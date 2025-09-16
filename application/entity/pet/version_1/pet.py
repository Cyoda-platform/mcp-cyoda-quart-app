"""
Pet Entity for Purrfect Pets API.

Represents a pet in the system with basic information and health status.
"""
from datetime import datetime, timezone
from typing import ClassVar, Optional
from pydantic import Field, validator

from entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity representing a pet in the Purrfect Pets system.
    
    Attributes:
        pet_id: Unique identifier for the pet
        name: Pet's name (max 100 characters)
        species: Type of animal (dog, cat, bird, fish, etc.)
        breed: Specific breed of the pet
        age: Age in years
        weight: Weight in kilograms
        color: Primary color of the pet
        gender: Male/Female/Unknown
        microchip_id: Microchip identification number
        owner_id: Reference to the pet's owner
        registration_date: When the pet was registered
        is_active: Whether the pet is still active in the system
        special_needs: Any special care requirements
        photo_url: URL to pet's photo
    """
    
    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Required fields
    pet_id: str = Field(..., description="Unique identifier for the pet")
    name: str = Field(..., max_length=100, description="Pet's name")
    species: str = Field(..., description="Type of animal (dog, cat, bird, fish, etc.)")
    owner_id: str = Field(..., description="Reference to the pet's owner")
    registration_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        description="When the pet was registered"
    )
    is_active: bool = Field(default=True, description="Whether the pet is still active in the system")
    
    # Optional fields
    breed: Optional[str] = Field(None, description="Specific breed of the pet")
    age: Optional[int] = Field(None, ge=0, le=30, description="Age in years")
    weight: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    color: Optional[str] = Field(None, description="Primary color of the pet")
    gender: Optional[str] = Field(None, description="Male/Female/Unknown")
    microchip_id: Optional[str] = Field(None, description="Microchip identification number")
    special_needs: Optional[str] = Field(None, description="Any special care requirements")
    photo_url: Optional[str] = Field(None, description="URL to pet's photo")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate pet name contains only valid characters."""
        if not v or not v.strip():
            raise ValueError("Pet name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Pet name cannot exceed 100 characters")
        return v.strip()
    
    @validator('species')
    def validate_species(cls, v):
        """Validate species is from approved list."""
        approved_species = {
            'dog', 'cat', 'bird', 'fish', 'rabbit', 'hamster', 'guinea pig',
            'ferret', 'turtle', 'snake', 'lizard', 'horse', 'goat', 'sheep'
        }
        if v.lower() not in approved_species:
            raise ValueError(f"Species must be one of: {', '.join(approved_species)}")
        return v.lower()
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender is one of the allowed values."""
        if v is not None:
            allowed_genders = {'male', 'female', 'unknown'}
            if v.lower() not in allowed_genders:
                raise ValueError(f"Gender must be one of: {', '.join(allowed_genders)}")
            return v.lower().capitalize()
        return v
    
    @validator('age')
    def validate_age(cls, v):
        """Validate age is reasonable."""
        if v is not None and (v < 0 or v > 30):
            raise ValueError("Pet age must be between 0 and 30 years")
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        """Validate weight is positive."""
        if v is not None and v <= 0:
            raise ValueError("Pet weight must be positive")
        return v
    
    def __str__(self) -> str:
        """String representation of the pet."""
        return f"Pet(pet_id={self.pet_id}, name={self.name}, species={self.species})"
