# entity/pet/version_1/pet.py

"""
Pet Entity for Cyoda Client Application

Represents a pet available in the Purrfect Pets store with workflow-managed availability status.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet represents a pet available in the Purrfect Pets store.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> available -> pending -> sold
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Pet's name")
    category: str = Field(..., description="Pet category reference")

    # Optional fields
    photo_urls: Optional[List[str]] = Field(
        default_factory=list, alias="photoUrls", description="List of photo URLs"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list, description="List of tags for categorization"
    )

    # Processing-related fields (populated during processing)
    availability_date: Optional[str] = Field(
        default=None,
        alias="availabilityDate",
        description="Date when pet became available",
    )
    reserved_date: Optional[str] = Field(
        default=None, alias="reservedDate", description="Date when pet was reserved"
    )
    sold_date: Optional[str] = Field(
        default=None, alias="soldDate", description="Date when pet was sold"
    )
    last_updated: Optional[str] = Field(
        default=None, alias="lastUpdated", description="Last update timestamp"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Pet name must be at most 50 characters long")
        return v.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet category must be non-empty")
        return v.strip()

    @field_validator("photo_urls")
    @classmethod
    def validate_photo_urls(cls, v: Optional[List[str]]) -> List[str]:
        """Validate photo URLs"""
        if v is None:
            return []
        # Basic URL validation - ensure they're not empty strings
        validated_urls = []
        for url in v:
            if url and url.strip():
                validated_urls.append(url.strip())
        return validated_urls

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> List[str]:
        """Validate tags"""
        if v is None:
            return []
        # Remove empty tags and strip whitespace
        validated_tags = []
        for tag in v:
            if tag and tag.strip():
                validated_tags.append(tag.strip())
        return validated_tags

    def update_timestamp(self) -> None:
        """Update the last_updated timestamp to current time"""
        self.last_updated = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_availability_date(self) -> None:
        """Set availability date and update timestamp"""
        self.availability_date = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_reserved_date(self) -> None:
        """Set reserved date and update timestamp"""
        self.reserved_date = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_sold_date(self) -> None:
        """Set sold date and update timestamp"""
        self.sold_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def clear_reserved_date(self) -> None:
        """Clear reserved date and update timestamp"""
        self.reserved_date = None
        self.update_timestamp()

    def is_available(self) -> bool:
        """Check if pet is available for purchase"""
        return self.state == "available"

    def is_pending(self) -> bool:
        """Check if pet is pending sale"""
        return self.state == "pending"

    def is_sold(self) -> bool:
        """Check if pet has been sold"""
        return self.state == "sold"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["meta"] = {"state": self.state}
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
