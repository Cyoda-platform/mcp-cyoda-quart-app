# entity/eggalarm/version_1/eggalarm.py

"""
EggAlarm for Cyoda Client Application

Represents an alarm set by a user for cooking eggs with different cooking types
and durations as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EggAlarm(CyodaEntity):
    """
    EggAlarm represents an alarm set by a user for cooking eggs.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: CREATED -> ACTIVE -> COMPLETED/CANCELLED/EXPIRED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EggAlarm"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    userId: str = Field(..., description="Identifier of the user who created the alarm")
    eggType: str = Field(..., description="Type of egg cooking (SOFT_BOILED, MEDIUM_BOILED, HARD_BOILED)")
    duration: int = Field(..., description="Cooking duration in seconds")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="When the alarm was created (ISO 8601 format)",
    )
    scheduledTime: Optional[str] = Field(
        default=None,
        description="When the alarm is scheduled to go off (ISO 8601 format)",
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional title for the alarm (defaults to egg type)",
    )
    isActive: bool = Field(
        default=False,
        description="Whether the alarm is currently active",
    )

    # Allowed egg types from functional requirements
    ALLOWED_EGG_TYPES: ClassVar[List[str]] = [
        "SOFT_BOILED",
        "MEDIUM_BOILED", 
        "HARD_BOILED",
    ]

    # Duration mapping for egg types (in seconds)
    EGG_TYPE_DURATIONS: ClassVar[Dict[str, int]] = {
        "SOFT_BOILED": 180,    # 3 minutes
        "MEDIUM_BOILED": 240,  # 4 minutes
        "HARD_BOILED": 360,    # 6 minutes
    }

    @field_validator("userId")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate userId field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID must be non-empty")
        return v.strip()

    @field_validator("eggType")
    @classmethod
    def validate_egg_type(cls, v: str) -> str:
        """Validate eggType field according to criteria requirements"""
        if v not in cls.ALLOWED_EGG_TYPES:
            raise ValueError(f"Egg type must be one of: {cls.ALLOWED_EGG_TYPES}")
        return v

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration field according to criteria requirements"""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title field"""
        if v is not None and len(v.strip()) == 0:
            return None  # Convert empty string to None
        return v.strip() if v else None

    def update_timestamp(self) -> None:
        """Update the createdAt timestamp to current time"""
        self.createdAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_scheduled_time(self, scheduled_time: str) -> None:
        """Set scheduled time and update timestamp"""
        self.scheduledTime = scheduled_time
        self.update_timestamp()

    def activate(self) -> None:
        """Activate the alarm and set scheduled time"""
        self.isActive = True
        current_time = datetime.now(timezone.utc)
        scheduled_time = current_time.timestamp() + self.duration
        self.scheduledTime = datetime.fromtimestamp(scheduled_time, timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def deactivate(self) -> None:
        """Deactivate the alarm"""
        self.isActive = False
        self.update_timestamp()

    def get_default_title(self) -> str:
        """Get default title based on egg type"""
        return f"{self.eggType.replace('_', ' ').title()} Eggs"

    def ensure_title(self) -> None:
        """Ensure title is set, using default if not provided"""
        if not self.title:
            self.title = self.get_default_title()

    def is_timer_elapsed(self) -> bool:
        """Check if the timer has elapsed"""
        if not self.scheduledTime or not self.isActive:
            return False
        
        current_time = datetime.now(timezone.utc)
        scheduled_time = datetime.fromisoformat(self.scheduledTime.replace("Z", "+00:00"))
        return current_time >= scheduled_time

    def is_notification_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if notification has expired (default 5 minutes)"""
        if not self.scheduledTime or not self.isActive:
            return False
        
        current_time = datetime.now(timezone.utc)
        scheduled_time = datetime.fromisoformat(self.scheduledTime.replace("Z", "+00:00"))
        expiration_time = scheduled_time.timestamp() + timeout_seconds
        return current_time.timestamp() >= expiration_time

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
