"""
Pet Entity for Purrfect Pets Application

Represents a pet available in the store with all required attributes
and relationships as specified in functional requirements.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents a pet available in the store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> draft -> available -> pending/sold/unavailable -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    name: str = Field(..., description="Name of the pet")
    photo_urls: List[str] = Field(..., alias="photoUrls", description="List of photo URLs for the pet")

    # Category relationship (stored as ID for performance)
    category_id: Optional[int] = Field(None, alias="categoryId", description="ID of the category the pet belongs to")
    category_name: Optional[str] = Field(None, alias="categoryName", description="Name of the category")

    # Tag relationships (stored as IDs for performance)
    tag_ids: Optional[List[int]] = Field(default_factory=list, alias="tagIds", description="List of tag IDs")
    tag_names: Optional[List[str]] = Field(default_factory=list, alias="tagNames", description="List of tag names")

    # Pet details
    description: Optional[str] = Field(None, description="Description of the pet")
    price: Optional[Decimal] = Field(None, description="Price of the pet")
    breed: Optional[str] = Field(None, description="Breed of the pet")
    age: Optional[int] = Field(None, description="Age of the pet in months")
    gender: Optional[str] = Field(None, description="Gender of the pet (MALE, FEMALE, UNKNOWN)")
    vaccinated: Optional[bool] = Field(None, description="Whether the pet is vaccinated")
    neutered: Optional[bool] = Field(None, description="Whether the pet is neutered/spayed")
    weight: Optional[Decimal] = Field(None, description="Weight of the pet in kg")
    color: Optional[str] = Field(None, description="Primary color of the pet")

    # Audit timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="When the pet was added to the system"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt", 
        description="When the pet was last updated"
    )

    # Validation constants
    VALID_GENDERS: ClassVar[List[str]] = ["MALE", "FEMALE", "UNKNOWN"]
    MAX_AGE_MONTHS: ClassVar[int] = 300  # 25 years
    MIN_PRICE: ClassVar[Decimal] = Decimal("0.01")
    MAX_WEIGHT_KG: ClassVar[Decimal] = Decimal("200.0")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name is required")
        if len(v.strip()) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Pet name must be at most 100 characters long")
        return v.strip()

    @field_validator("photo_urls")
    @classmethod
    def validate_photo_urls(cls, v: List[str]) -> List[str]:
        """Validate photo URLs"""
        if not v or len(v) == 0:
            raise ValueError("At least one photo URL is required")
        
        for url in v:
            if not url or len(url.strip()) == 0:
                raise ValueError("Photo URLs cannot be empty")
            if not url.startswith(("http://", "https://")):
                raise ValueError("Photo URLs must be valid HTTP/HTTPS URLs")
        
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate pet price"""
        if v is not None:
            if v < cls.MIN_PRICE:
                raise ValueError(f"Price must be at least {cls.MIN_PRICE}")
            if v > Decimal("999999.99"):
                raise ValueError("Price cannot exceed 999,999.99")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate pet age"""
        if v is not None:
            if v < 0:
                raise ValueError("Age cannot be negative")
            if v > cls.MAX_AGE_MONTHS:
                raise ValueError(f"Age cannot exceed {cls.MAX_AGE_MONTHS} months")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        """Validate pet gender"""
        if v is not None:
            if v not in cls.VALID_GENDERS:
                raise ValueError(f"Gender must be one of: {cls.VALID_GENDERS}")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate pet weight"""
        if v is not None:
            if v <= 0:
                raise ValueError("Weight must be positive")
            if v > cls.MAX_WEIGHT_KG:
                raise ValueError(f"Weight cannot exceed {cls.MAX_WEIGHT_KG} kg")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_available(self) -> bool:
        """Check if pet is available for purchase"""
        return self.state == "available"

    def is_pending(self) -> bool:
        """Check if pet is pending (reserved)"""
        return self.state == "pending"

    def is_sold(self) -> bool:
        """Check if pet is sold"""
        return self.state == "sold"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
