"""
Category Entity for Purrfect Pets API

Represents a category for organizing pets as specified in the functional requirements.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category entity representing pet categories.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Category name", max_length=50)
    description: str = Field(..., description="Category description", max_length=200)

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the category was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the category was last updated (ISO 8601 format)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name must be non-empty")
        if len(v) > 50:
            raise ValueError("Category name must be at most 50 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category description must be non-empty")
        if len(v) > 200:
            raise ValueError("Category description must be at most 200 characters long")
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_active(self) -> bool:
        """Check if category is active"""
        return self.state == "active"

    def is_inactive(self) -> bool:
        """Check if category is inactive"""
        return self.state == "inactive"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
