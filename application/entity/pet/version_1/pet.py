"""
Pet Entity for Purrfect Pets API

Represents a pet in the Purrfect Pets store with all its characteristics and current availability status.
The Pet entity uses workflow states managed by the system.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet represents a pet in the Purrfect Pets store with all its characteristics.
    
    The Pet entity uses `status` semantically as its state, which will be managed 
    by the system as `entity.meta.state`. The possible states are:
    - `available`: Pet is available for purchase
    - `pending`: Pet is reserved/pending adoption  
    - `sold`: Pet has been sold/adopted
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Name of the pet (required)")
    category: Dict[str, Any] = Field(..., description="Category the pet belongs to")
    photoUrls: List[str] = Field(..., alias="photoUrls", description="List of photo URLs for the pet (required)")
    
    # Optional fields
    tags: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of tags associated with the pet")
    description: Optional[str] = Field(default=None, description="Additional description of the pet")
    price: Optional[Decimal] = Field(default=None, description="Price of the pet")
    birthDate: Optional[date] = Field(default=None, alias="birthDate", description="Birth date of the pet")
    breed: Optional[str] = Field(default=None, description="Breed of the pet")
    color: Optional[str] = Field(default=None, description="Color of the pet")
    weight: Optional[float] = Field(default=None, description="Weight of the pet in kg")
    vaccinated: Optional[bool] = Field(default=None, description="Whether the pet is vaccinated")
    neutered: Optional[bool] = Field(default=None, description="Whether the pet is neutered/spayed")
    
    # Processing-related fields (populated during processing)
    reservedBy: Optional[str] = Field(default=None, alias="reservedBy", description="Customer ID who reserved the pet")
    reservationExpiry: Optional[str] = Field(default=None, alias="reservationExpiry", description="Reservation expiry timestamp")
    soldDate: Optional[date] = Field(default=None, alias="soldDate", description="Date when pet was sold")
    soldTo: Optional[str] = Field(default=None, alias="soldTo", description="Customer ID who bought the pet")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Pet name must be at most 100 characters long")
        return v.strip()

    @field_validator("photoUrls")
    @classmethod
    def validate_photo_urls(cls, v: List[str]) -> List[str]:
        """Validate photoUrls field"""
        if not v or len(v) == 0:
            raise ValueError("Pet must have at least one photo URL")
        for url in v:
            if not url or len(url.strip()) == 0:
                raise ValueError("Photo URLs must be non-empty")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate category field"""
        if not v or "id" not in v:
            raise ValueError("Category must have an id field")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate price field"""
        if v is not None and v < 0:
            raise ValueError("Pet price must be non-negative")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Optional[float]) -> Optional[float]:
        """Validate weight field"""
        if v is not None and v <= 0:
            raise ValueError("Pet weight must be positive")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Additional business validation can be added here
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_available(self) -> bool:
        """Check if pet is available for reservation or sale"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is currently reserved"""
        return self.state == "pending"

    def is_sold(self) -> bool:
        """Check if pet has been sold"""
        return self.state == "sold"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
