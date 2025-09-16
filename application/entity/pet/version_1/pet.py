"""
Pet Entity for Purrfect Pets API

Represents a pet available for adoption with all required attributes
including category, photos, tags, breed information, and pricing.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity representing animals available for adoption.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: Available -> Pending -> Sold
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Pet name", max_length=100)
    category_id: int = Field(..., description="Foreign key to Category")
    photo_urls: List[str] = Field(
        default_factory=list, description="URLs to pet photos"
    )
    tags: List[str] = Field(
        default_factory=list, description="Pet tags for categorization"
    )
    breed: str = Field(..., description="Pet breed", max_length=50)
    age: int = Field(..., description="Pet age in years", ge=0, le=50)
    weight: float = Field(..., description="Pet weight in kg", gt=0)
    color: str = Field(..., description="Pet color", max_length=30)
    description: str = Field(..., description="Pet description", max_length=500)
    price: float = Field(..., description="Pet price", ge=0)
    vaccination_status: bool = Field(..., description="Whether pet is vaccinated")

    # Timestamps (inherited from CyodaEntity but override for consistency)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the pet was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the pet was last updated (ISO 8601 format)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) > 100:
            raise ValueError("Pet name must be at most 100 characters long")
        return v.strip()

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: str) -> str:
        """Validate pet breed"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet breed must be non-empty")
        if len(v) > 50:
            raise ValueError("Pet breed must be at most 50 characters long")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate pet color"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet color must be non-empty")
        if len(v) > 30:
            raise ValueError("Pet color must be at most 30 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate pet description"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet description must be non-empty")
        if len(v) > 500:
            raise ValueError("Pet description must be at most 500 characters long")
        return v.strip()

    @field_validator("photo_urls")
    @classmethod
    def validate_photo_urls(cls, v: List[str]) -> List[str]:
        """Validate photo URLs"""
        if not v:
            return v

        for url in v:
            if not url or not url.strip():
                raise ValueError("Photo URLs must be non-empty")
            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ValueError("Photo URLs must be valid HTTP/HTTPS URLs")

        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_available(self) -> bool:
        """Check if pet is available for adoption"""
        return self.state == "Available"

    def is_pending(self) -> bool:
        """Check if pet is pending (reserved for an order)"""
        return self.state == "Pending"

    def is_sold(self) -> bool:
        """Check if pet has been sold"""
        return self.state == "Sold"

    def to_api_response(self) -> dict:
        """Convert to API response format"""
        data = self.model_dump()
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
