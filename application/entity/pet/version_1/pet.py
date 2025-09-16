"""
Pet Entity for Purrfect Pets API

Represents a pet available for adoption with all required attributes
and workflow state management as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents a pet available for adoption in the Purrfect Pets system.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> available -> reserved -> adopted
    or available -> medical_hold -> available or available -> unavailable -> available
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
        default=None, alias="imageUrl", description="URL to pet's photo"
    )
    vaccinated: bool = Field(default=False, description="Vaccination status")
    neutered: bool = Field(default=False, description="Neutering status")
    microchipped: bool = Field(default=False, description="Microchip status")
    special_needs: Optional[str] = Field(
        default=None, alias="specialNeeds", description="Any special care requirements"
    )
    arrival_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="arrivalDate",
        description="When pet arrived at store (ISO 8601 format)",
    )
    adopter_id: Optional[int] = Field(
        default=None,
        alias="adopterId",
        description="ID of adopter, null if not adopted",
    )

    # Validation constants
    ALLOWED_CATEGORIES: ClassVar[list[str]] = [
        "Dog",
        "Cat",
        "Bird",
        "Fish",
        "Rabbit",
        "Hamster",
        "Guinea Pig",
        "Reptile",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Name must be at most 50 characters long")
        return v.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category field"""
        if v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: str) -> str:
        """Validate breed field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Breed must be non-empty")
        if len(v) > 50:
            raise ValueError("Breed must be at most 50 characters long")
        return v.strip()

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age field"""
        if v < 0:
            raise ValueError("Age must be non-negative")
        if v > 30:
            raise ValueError("Age must be at most 30 years")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Color must be non-empty")
        if len(v) > 30:
            raise ValueError("Color must be at most 30 characters long")
        return v.strip()

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """Validate weight field"""
        if v <= 0:
            raise ValueError("Weight must be positive")
        if v > 200:
            raise ValueError("Weight must be at most 200 kg")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price field"""
        if v < 0:
            raise ValueError("Price must be non-negative")
        if v > 10000:
            raise ValueError("Price must be at most $10,000")
        return v

    @field_validator("special_needs")
    @classmethod
    def validate_special_needs(cls, v: Optional[str]) -> Optional[str]:
        """Validate special_needs field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Special needs must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    def is_available_for_adoption(self) -> bool:
        """Check if pet is available for adoption"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is reserved"""
        return self.state == "reserved"

    def is_adopted(self) -> bool:
        """Check if pet has been adopted"""
        return self.state == "adopted"

    def is_on_medical_hold(self) -> bool:
        """Check if pet is on medical hold"""
        return self.state == "medical_hold"

    def is_unavailable(self) -> bool:
        """Check if pet is unavailable"""
        return self.state == "unavailable"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
