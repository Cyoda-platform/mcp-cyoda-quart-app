"""
Pet Entity for Cyoda Client Application

Represents a pet from the petstore API with analysis capabilities.
Loads data from petstore API and performs pandas-based analysis.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(BaseModel):
    """Category model for Pet entity"""
    id: Optional[int] = Field(default=None, description="Category ID")
    name: Optional[str] = Field(default=None, description="Category name")


class Tag(BaseModel):
    """Tag model for Pet entity"""
    id: Optional[int] = Field(default=None, description="Tag ID")
    name: Optional[str] = Field(default=None, description="Tag name")


class Pet(CyodaEntity):
    """
    Pet entity represents a pet from the petstore API with analysis capabilities.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> loaded -> analyzed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Pet data fields from petstore API
    pet_id: Optional[int] = Field(
        default=None,
        alias="petId", 
        description="Pet ID from petstore API"
    )
    name: str = Field(..., description="Pet name (required)")
    category: Optional[Category] = Field(
        default=None, 
        description="Pet category"
    )
    photo_urls: List[str] = Field(
        default_factory=list,
        alias="photoUrls",
        description="List of photo URLs"
    )
    tags: List[Tag] = Field(
        default_factory=list,
        description="List of tags"
    )
    status: Optional[str] = Field(
        default=None,
        description="Pet status (available, pending, sold)"
    )

    # Analysis results fields
    analysis_results: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="analysisResults",
        description="Results from pandas analysis"
    )
    data_source: Optional[str] = Field(
        default="petstore_api",
        alias="dataSource",
        description="Source of the pet data"
    )
    load_timestamp: Optional[str] = Field(
        default=None,
        alias="loadTimestamp",
        description="Timestamp when data was loaded from API"
    )
    analysis_timestamp: Optional[str] = Field(
        default=None,
        alias="analysisTimestamp", 
        description="Timestamp when analysis was performed"
    )

    # Timestamps (inherited from CyodaEntity but with aliases)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the entity was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the entity was last updated (ISO 8601 format)",
    )

    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate pet status field"""
        if v is None:
            return v
        allowed_statuses = ["available", "pending", "sold"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name field"""
        if not v or len(v.strip()) < 1:
            raise ValueError("Pet name cannot be empty")
        if len(v) > 100:
            raise ValueError("Pet name cannot exceed 100 characters")
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_load_timestamp(self) -> None:
        """Set the load timestamp to current time"""
        self.load_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_analysis_timestamp(self) -> None:
        """Set the analysis timestamp to current time"""
        self.analysis_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_analysis_results(self, results: Dict[str, Any]) -> None:
        """Set analysis results and update timestamp"""
        self.analysis_results = results
        self.set_analysis_timestamp()

    def is_loaded(self) -> bool:
        """Check if pet data has been loaded"""
        return self.load_timestamp is not None

    def is_analyzed(self) -> bool:
        """Check if pet data has been analyzed"""
        return self.analysis_results is not None

    def get_category_name(self) -> str:
        """Get category name or default"""
        if self.category and self.category.name:
            return self.category.name
        return "Unknown"

    def get_tag_names(self) -> List[str]:
        """Get list of tag names"""
        return [tag.name for tag in self.tags if tag.name]

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data: Dict[str, Any] = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data
