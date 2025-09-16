"""
Category Entity for Purrfect Pets Application

Represents a category of pets with all required attributes
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category entity represents a category of pets.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    name: str = Field(..., description="Name of the category")

    # Optional fields
    description: Optional[str] = Field(None, description="Description of the category")
    image_url: Optional[str] = Field(None, alias="imageUrl", description="Image URL for the category")

    # Audit timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="When the category was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="When the category was last updated"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate category name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name is required")
        if len(v.strip()) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Category name must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Category description must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate image URL"""
        if v is not None:
            if not v.strip():
                return None
            if not v.startswith(("http://", "https://")):
                raise ValueError("Image URL must be a valid HTTP/HTTPS URL")
            return v.strip()
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_active(self) -> bool:
        """Check if category is active"""
        return self.state == "active"

    def is_inactive(self) -> bool:
        """Check if category is inactive"""
        return self.state == "inactive"

    def is_archived(self) -> bool:
        """Check if category is archived"""
        return self.state == "archived"

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
