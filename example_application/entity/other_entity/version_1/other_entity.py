"""
OtherEntity for Cyoda Client Application

Represents a secondary business object that gets updated by ExampleEntity processing
and has its own simple workflow as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class OtherEntity(CyodaEntity):
    """
    OtherEntity represents a secondary business object that gets updated by
    ExampleEntity processing and has its own simple workflow.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> pending -> active -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "OtherEntity"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    title: str = Field(..., description="Title of the other entity")
    content: str = Field(..., description="Content or data of the entity")
    priority: str = Field(..., description="Priority level (LOW, MEDIUM, HIGH)")
    source_entity_id: Optional[str] = Field(
        default=None,
        alias="sourceEntityId",
        description="Reference to the ExampleEntity that updated this entity",
    )
    last_updated_by: Optional[str] = Field(
        default=None,
        alias="lastUpdatedBy",
        description="Identifier of the entity that last updated this one",
    )

    # Timestamps (inherited created_at from CyodaEntity, but need to override updated_at behavior)
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

    # Priority validation
    ALLOWED_PRIORITIES: ClassVar[List[str]] = ["LOW", "MEDIUM", "HIGH"]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Title must be non-empty")
        if len(v) > 200:
            raise ValueError("Title must be at most 200 characters long")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Content must be non-empty")
        if len(v) > 1000:
            raise ValueError("Content must be at most 1000 characters long")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority field"""
        if v not in cls.ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of: {cls.ALLOWED_PRIORITIES}")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_source_entity(
        self, source_entity_id: str, updated_by: Optional[str] = None
    ) -> None:
        """Set source entity information and update timestamp"""
        self.source_entity_id = source_entity_id
        if updated_by:
            self.last_updated_by = updated_by
        self.update_timestamp()

    def is_pending(self) -> bool:
        """Check if entity is in pending state"""
        return self.state == "pending"

    def is_active(self) -> bool:
        """Check if entity is in active state"""
        return self.state == "active"

    def is_archived(self) -> bool:
        """Check if entity is in archived state"""
        return self.state == "archived"

    def get_priority_level(self) -> int:
        """Get numeric priority level for sorting"""
        priority_levels: Dict[str, int] = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        return priority_levels.get(self.priority, 0)

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data: Dict[str, Any] = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
