# entity/category/version_1/category.py

"""
Category Entity for Cyoda Client Application

Represents a pet category for organizing pets in the Purrfect Pets store.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category represents a pet category for organizing pets in the Purrfect Pets store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> draft -> active -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Category name")
    
    # Optional fields
    description: Optional[str] = Field(
        default=None,
        description="Category description"
    )
    
    # Processing-related fields (populated during processing)
    created_date: Optional[str] = Field(
        default=None,
        alias="createdDate",
        description="Date when category was created"
    )
    published_date: Optional[str] = Field(
        default=None,
        alias="publishedDate",
        description="Date when category was published"
    )
    archived_date: Optional[str] = Field(
        default=None,
        alias="archivedDate",
        description="Date when category was archived"
    )
    last_updated: Optional[str] = Field(
        default=None,
        alias="lastUpdated",
        description="Last update timestamp"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name must be non-empty")
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Category name must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 500:
            raise ValueError("Category description must be at most 500 characters long")
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the last_updated timestamp to current time"""
        self.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_created_date(self) -> None:
        """Set created date and update timestamp"""
        self.created_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_published_date(self) -> None:
        """Set published date and update timestamp"""
        self.published_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_archived_date(self) -> None:
        """Set archived date and update timestamp"""
        self.archived_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def clear_archived_date(self) -> None:
        """Clear archived date and update timestamp"""
        self.archived_date = None
        self.update_timestamp()

    def is_draft(self) -> bool:
        """Check if category is in draft state"""
        return self.state == "draft"

    def is_active(self) -> bool:
        """Check if category is active"""
        return self.state == "active"

    def is_archived(self) -> bool:
        """Check if category is archived"""
        return self.state == "archived"

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
