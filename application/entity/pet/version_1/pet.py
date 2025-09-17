# entity/pet/version_1/pet.py

"""
Pet Entity for Purrfect Pets API

Represents a pet in the adoption system with all required attributes
and state management through Cyoda workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents a pet available for adoption in the Purrfect Pets system.
    
    The Pet entity uses entity.meta.state to track its lifecycle status:
    - AVAILABLE: Pet is available for adoption
    - RESERVED: Pet is reserved for an approved adoption application
    - ADOPTED: Pet has been adopted
    - MEDICAL_HOLD: Pet is on medical hold for health issues
    - UNAVAILABLE: Pet is temporarily unavailable
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Pet's name")
    category: str = Field(..., description="Pet category (e.g., Dog, Cat, Bird, Fish)")
    breed: str = Field(..., description="Specific breed")
    age: int = Field(..., description="Age in years")
    color: str = Field(..., description="Primary color")
    weight: float = Field(..., description="Weight in kg")
    description: str = Field(..., description="Detailed description")
    price: float = Field(..., description="Price in USD")
    
    # Optional fields
    image_url: Optional[str] = Field(
        default=None,
        alias="imageUrl",
        description="URL to pet's photo"
    )
    vaccinated: bool = Field(default=False, description="Vaccination status")
    neutered: bool = Field(default=False, description="Neutering status")
    microchipped: bool = Field(default=False, description="Microchip status")
    special_needs: Optional[str] = Field(
        default=None,
        alias="specialNeeds",
        description="Any special care requirements"
    )
    
    # Timestamp fields
    arrival_date: Optional[str] = Field(
        default=None,
        alias="arrivalDate",
        description="When pet arrived at store (ISO 8601 format)"
    )
    adoption_date: Optional[str] = Field(
        default=None,
        alias="adoptionDate",
        description="When pet was adopted (ISO 8601 format)"
    )

    # Validation rules
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("Pet name must be at most 100 characters")
        return v.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet category must be non-empty")
        return v.strip()

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: str) -> str:
        """Validate breed field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet breed must be non-empty")
        return v.strip()

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age field"""
        if v < 0:
            raise ValueError("Pet age must be non-negative")
        if v > 50:
            raise ValueError("Pet age must be reasonable (max 50 years)")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Validate weight field"""
        if v <= 0:
            raise ValueError("Pet weight must be positive")
        if v > 500:
            raise ValueError("Pet weight must be reasonable (max 500 kg)")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price field"""
        if v < 0:
            raise ValueError("Pet price must be non-negative")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Pet description must be at most 1000 characters")
        return v.strip()

    def set_arrival_date(self) -> None:
        """Set arrival date to current timestamp"""
        self.arrival_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_adoption_date(self) -> None:
        """Set adoption date to current timestamp"""
        self.adoption_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_available(self) -> bool:
        """Check if pet is available for adoption"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is reserved"""
        return self.state == "reserved"

    def is_adopted(self) -> bool:
        """Check if pet is adopted"""
        return self.state == "adopted"

    def is_on_medical_hold(self) -> bool:
        """Check if pet is on medical hold"""
        return self.state == "medical_hold"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
