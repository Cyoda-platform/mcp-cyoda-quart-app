# entity/position/version_1/position.py

"""
Position Entity for Cyoda Client Application

Represents job positions and titles within the organization
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Position(CyodaEntity):
    """
    Position represents job positions and titles within the organization.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Position"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    title: str = Field(..., description="Position title (unique within department)")
    description: str = Field(..., description="Position description")
    department: str = Field(..., description="Department name")
    
    # Optional fields
    level: Optional[str] = Field(
        default=None,
        description="Position level/grade"
    )
    salary_range_min: Optional[float] = Field(
        default=None,
        description="Minimum salary"
    )
    salary_range_max: Optional[float] = Field(
        default=None,
        description="Maximum salary"
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Position status flag"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the entity was last updated (ISO 8601 format)"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Position title must be non-empty")
        if len(v) < 2:
            raise ValueError("Position title must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Position title must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Position description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Position description must be at most 1000 characters long")
        return v.strip()

    @field_validator("department")
    @classmethod
    def validate_department(cls, v: str) -> str:
        """Validate department field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Department must be non-empty")
        if len(v) > 100:
            raise ValueError("Department must be at most 100 characters long")
        return v.strip()

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate level field"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v) > 50:
            raise ValueError("Position level must be at most 50 characters long")
        return v.strip()

    @field_validator("salary_range_min")
    @classmethod
    def validate_salary_range_min(cls, v: Optional[float]) -> Optional[float]:
        """Validate minimum salary field"""
        if v is None:
            return v
        if v < 0:
            raise ValueError("Minimum salary must be non-negative")
        return v

    @field_validator("salary_range_max")
    @classmethod
    def validate_salary_range_max(cls, v: Optional[float]) -> Optional[float]:
        """Validate maximum salary field"""
        if v is None:
            return v
        if v < 0:
            raise ValueError("Maximum salary must be non-negative")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Position":
        """Validate business logic rules according to functional requirements"""
        # Validate salary range
        if (self.salary_range_min is not None and 
            self.salary_range_max is not None and 
            self.salary_range_min > self.salary_range_max):
            raise ValueError("Minimum salary must be less than or equal to maximum salary")
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_position_active(self) -> bool:
        """Check if position is active and can be assigned"""
        return self.is_active is True and self.state == "active"

    def has_salary_range(self) -> bool:
        """Check if position has a defined salary range"""
        return (self.salary_range_min is not None and 
                self.salary_range_max is not None)

    def get_salary_range_display(self) -> str:
        """Get formatted salary range for display"""
        if not self.has_salary_range():
            return "Not specified"
        return f"${self.salary_range_min:,.2f} - ${self.salary_range_max:,.2f}"

    def get_position_key(self) -> str:
        """Get unique position key combining department and title"""
        return f"{self.department}.{self.title}".lower().replace(" ", "_")

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["has_salary_range"] = self.has_salary_range()
        data["salary_range_display"] = self.get_salary_range_display()
        data["position_key"] = self.get_position_key()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
