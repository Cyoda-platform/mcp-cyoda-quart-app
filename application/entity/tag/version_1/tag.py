"""
Tag Entity for Purrfect Pets Application

Represents tags that can be associated with pets
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Tag(CyodaEntity):
    """
    Tag entity represents tags that can be associated with pets.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Tag"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    name: str = Field(..., description="Name of the tag")

    # Optional fields
    color: Optional[str] = Field(None, description="Color code for the tag display")
    description: Optional[str] = Field(None, description="Description of the tag")

    # Audit timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="When the tag was created"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tag name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Tag name is required")
        if len(v.strip()) < 2:
            raise ValueError("Tag name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Tag name must be at most 50 characters long")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color code"""
        if v is not None:
            if not v.strip():
                return None
            # Basic hex color validation
            v = v.strip()
            if not v.startswith("#"):
                raise ValueError("Color must be a hex color code starting with #")
            if len(v) not in [4, 7]:  # #RGB or #RRGGBB
                raise ValueError("Color must be a valid hex color code (#RGB or #RRGGBB)")
            try:
                int(v[1:], 16)  # Validate hex digits
            except ValueError:
                raise ValueError("Color must contain valid hexadecimal digits")
            return v.upper()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate tag description"""
        if v is not None:
            if len(v) > 200:
                raise ValueError("Tag description must be at most 200 characters long")
            return v.strip() if v.strip() else None
        return v

    def is_active(self) -> bool:
        """Check if tag is active"""
        return self.state == "active"

    def is_inactive(self) -> bool:
        """Check if tag is inactive"""
        return self.state == "inactive"

    def is_archived(self) -> bool:
        """Check if tag is archived"""
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
