"""
Pet Entity for Purrfect Pets API

Represents a pet in the store inventory with all required attributes
and relationships as specified in functional requirements.
"""

from datetime import date
from decimal import Decimal
from typing import ClassVar, List, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """Category reference for Pet entity"""

    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    id: Optional[int] = Field(None, description="Category ID")
    name: Optional[str] = Field(None, description="Category name")


class Tag(CyodaEntity):
    """Tag reference for Pet entity"""

    ENTITY_NAME: ClassVar[str] = "Tag"
    ENTITY_VERSION: ClassVar[int] = 1

    id: Optional[int] = Field(None, description="Tag ID")
    name: Optional[str] = Field(None, description="Tag name")


class Pet(CyodaEntity):
    """
    Pet entity represents a pet in the store inventory.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: AVAILABLE, PENDING, SOLD, RESERVED, UNAVAILABLE
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the pet")
    name: str = Field(..., description="Name of the pet (required)")
    category: Optional[Category] = Field(
        None, description="Category the pet belongs to"
    )
    photo_urls: List[str] = Field(
        ..., alias="photoUrls", description="List of photo URLs for the pet (required)"
    )
    tags: Optional[List[Tag]] = Field(
        default_factory=list, description="List of tags associated with the pet"
    )

    # Optional fields
    description: Optional[str] = Field(None, description="Description of the pet")
    price: Optional[Decimal] = Field(None, description="Price of the pet")
    birth_date: Optional[date] = Field(
        None, alias="birthDate", description="Birth date of the pet"
    )
    breed: Optional[str] = Field(None, description="Breed of the pet")
    weight: Optional[float] = Field(None, description="Weight of the pet in kg")
    vaccinated: Optional[bool] = Field(
        None, description="Whether the pet is vaccinated"
    )
    neutered: Optional[bool] = Field(
        None, description="Whether the pet is neutered/spayed"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name is required and cannot be empty")
        return v.strip()

    @field_validator("photo_urls")
    @classmethod
    def validate_photo_urls(cls, v: List[str]) -> List[str]:
        """Validate photo URLs field"""
        if not v or len(v) == 0:
            raise ValueError("At least one photo URL is required")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate price field"""
        if v is not None and v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate birth date field"""
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        """Validate weight field"""
        if v is not None and v <= 0:
            raise ValueError("Weight must be positive")
        return v

    def is_available(self) -> bool:
        """Check if pet is available for purchase"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is reserved"""
        return self.state in ["pending", "reserved"]

    def is_sold(self) -> bool:
        """Check if pet is sold"""
        return self.state == "sold"

    def get_status(self) -> str:
        """Get pet status based on state"""
        state_mapping = {
            "available": "AVAILABLE",
            "pending": "PENDING",
            "reserved": "RESERVED",
            "sold": "SOLD",
            "unavailable": "UNAVAILABLE",
        }
        return state_mapping.get(self.state, "UNKNOWN")
