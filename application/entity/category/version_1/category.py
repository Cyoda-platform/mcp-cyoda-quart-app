"""
Category Entity for Purrfect Pets API Application

Represents a pet category in the pet store for organizing pets by type.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category entity represents a pet category in the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> validated -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    name: str = Field(..., description="Name of the category")

    # Optional fields
    description: Optional[str] = Field(
        default=None,
        description="Description of the category"
    )

    # Processing-related fields
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data populated during processing"
    )

    # Validation constants
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "Dogs", "Cats", "Birds", "Fish", "Reptiles", "Small Animals", "Other"
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate category name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name must be non-empty")
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Category name must be at most 50 characters long")
        if v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description"""
        if v is not None:
            if len(v) > 200:
                raise ValueError("Description must be at most 200 characters long")
            return v.strip()
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

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
