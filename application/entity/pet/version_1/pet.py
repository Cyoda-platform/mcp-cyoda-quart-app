"""
Pet Entity for Product Performance Analysis and Reporting System

Represents a pet from the Pet Store API with fields for performance analysis.
Extends CyodaEntity to integrate with Cyoda workflow system.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(BaseModel):
    """Pet category model matching Pet Store API structure"""

    id: Optional[int] = Field(None, description="Category ID")
    name: str = Field(..., description="Category name")


class Tag(BaseModel):
    """Pet tag model matching Pet Store API structure"""

    id: Optional[int] = Field(None, description="Tag ID")
    name: str = Field(..., description="Tag name")


class Pet(CyodaEntity):
    """
    Pet entity representing pets from the Pet Store API.

    This entity stores pet data retrieved from https://petstore.swagger.io/v2/
    and is used for performance analysis and reporting.

    Inherits from CyodaEntity to get workflow management capabilities.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core pet fields from Pet Store API
    pet_id: Optional[int] = Field(
        None, alias="petId", description="Pet ID from Pet Store API"
    )
    name: str = Field(..., description="Pet name")
    category: Optional[Dict[str, Any]] = Field(
        None, description="Pet category (id and name)"
    )
    photo_urls: List[str] = Field(
        default_factory=list,
        alias="photoUrls",
        description="List of photo URLs for the pet",
    )
    tags: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of tags (id and name pairs)"
    )
    status: Optional[str] = Field(
        None, description="Pet status in the store (available, pending, sold)"
    )

    # Performance analysis fields
    performance_score: Optional[float] = Field(
        None,
        alias="performanceScore",
        description="Calculated performance score for this pet",
    )
    analysis_data: Optional[Dict[str, Any]] = Field(
        None, alias="analysisData", description="Performance analysis results"
    )
    last_analyzed_at: Optional[str] = Field(
        None,
        alias="lastAnalyzedAt",
        description="Timestamp when performance analysis was last run",
    )

    # Validation constants
    VALID_STATUSES: ClassVar[List[str]] = ["available", "pending", "sold"]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) > 255:
            raise ValueError("Pet name must be at most 255 characters")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate pet status"""
        if v is not None and v not in cls.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {cls.VALID_STATUSES}")
        return v

    @field_validator("performance_score")
    @classmethod
    def validate_performance_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate performance score"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("Performance score must be between 0.0 and 100.0")
        return v

    def update_analysis_data(self, analysis_data: Dict[str, Any]) -> None:
        """Update analysis data and timestamp"""
        self.analysis_data = analysis_data
        self.last_analyzed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_performance_score(self, score: float) -> None:
        """Set performance score with validation"""
        if score < 0.0 or score > 100.0:
            raise ValueError("Performance score must be between 0.0 and 100.0")
        self.performance_score = score
        self.update_timestamp()

    def is_available(self) -> bool:
        """Check if pet is available for sale"""
        return self.status == "available"

    def is_analyzed(self) -> bool:
        """Check if pet has been analyzed"""
        return self.analysis_data is not None and self.last_analyzed_at is not None

    def get_category_name(self) -> Optional[str]:
        """Get category name if category exists"""
        if self.category and isinstance(self.category, dict):
            return self.category.get("name")
        return None

    def get_tag_names(self) -> List[str]:
        """Get list of tag names"""
        tag_names = []
        for tag in self.tags:
            if isinstance(tag, dict) and "name" in tag:
                tag_names.append(tag["name"])
        return tag_names

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
