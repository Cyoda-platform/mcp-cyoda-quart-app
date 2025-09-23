# entity/egg_alarm/version_1/egg_alarm.py

"""
EggAlarm Entity for Cyoda Client Application

Represents an egg cooking alarm that allows users to choose between different
egg types (soft-boiled, medium-boiled, hard-boiled) and set cooking alarms.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class EggType(str, Enum):
    """Enumeration of supported egg cooking types"""
    SOFT_BOILED = "soft-boiled"
    MEDIUM_BOILED = "medium-boiled"
    HARD_BOILED = "hard-boiled"


class AlarmStatus(str, Enum):
    """Enumeration of alarm status values"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EggAlarm(CyodaEntity):
    """
    EggAlarm represents an egg cooking alarm that manages timing for different
    egg cooking types with workflow-managed states.
    
    The state field manages workflow states: 
    initial_state -> created -> scheduled -> active -> completed/cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EggAlarm"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core alarm fields
    egg_type: EggType = Field(
        ..., 
        description="Type of egg cooking: soft-boiled, medium-boiled, or hard-boiled"
    )
    cooking_duration: int = Field(
        ..., 
        description="Cooking duration in minutes for the selected egg type"
    )
    alarm_time: Optional[str] = Field(
        default=None,
        alias="alarmTime",
        description="ISO 8601 timestamp when the alarm should trigger"
    )
    status: AlarmStatus = Field(
        default=AlarmStatus.PENDING,
        description="Current status of the alarm"
    )
    
    # User and metadata fields
    created_by: str = Field(
        ...,
        alias="createdBy", 
        description="User who created the alarm"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional user notes about the alarm"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the alarm was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the alarm was last updated (ISO 8601 format)",
    )
    
    # Processing fields (populated during workflow processing)
    scheduled_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="scheduledData",
        description="Data populated when alarm is scheduled"
    )
    completion_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="completionData", 
        description="Data populated when alarm completes"
    )

    # Cooking duration mappings
    COOKING_DURATIONS: ClassVar[Dict[EggType, int]] = {
        EggType.SOFT_BOILED: 4,    # 4 minutes
        EggType.MEDIUM_BOILED: 7,  # 7 minutes  
        EggType.HARD_BOILED: 10,   # 10 minutes
    }

    @field_validator("egg_type")
    @classmethod
    def validate_egg_type(cls, v: EggType) -> EggType:
        """Validate egg type is supported"""
        if v not in cls.COOKING_DURATIONS:
            raise ValueError(f"Unsupported egg type: {v}")
        return v

    @field_validator("cooking_duration")
    @classmethod
    def validate_cooking_duration(cls, v: int) -> int:
        """Validate cooking duration is reasonable"""
        if v < 1:
            raise ValueError("Cooking duration must be at least 1 minute")
        if v > 30:
            raise ValueError("Cooking duration must be at most 30 minutes")
        return v

    @field_validator("created_by")
    @classmethod
    def validate_created_by(cls, v: str) -> str:
        """Validate created_by field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Created by field must be non-empty")
        if len(v) > 100:
            raise ValueError("Created by field must be at most 100 characters")
        return v.strip()

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes field if provided"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Notes must be at most 500 characters")
            return v.strip() if v.strip() else None
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "EggAlarm":
        """Validate business logic rules"""
        # Auto-set cooking duration based on egg type if not provided or incorrect
        expected_duration = self.COOKING_DURATIONS.get(self.egg_type)
        if expected_duration and self.cooking_duration != expected_duration:
            self.cooking_duration = expected_duration

        # Validate alarm time format if provided
        if self.alarm_time:
            try:
                datetime.fromisoformat(self.alarm_time.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Alarm time must be in ISO 8601 format")

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_scheduled_data(self, scheduled_data: Dict[str, Any]) -> None:
        """Set scheduled data and update timestamp"""
        self.scheduled_data = scheduled_data
        self.status = AlarmStatus.SCHEDULED
        self.update_timestamp()

    def set_completion_data(self, completion_data: Dict[str, Any]) -> None:
        """Set completion data and update timestamp"""
        self.completion_data = completion_data
        self.status = AlarmStatus.COMPLETED
        self.update_timestamp()

    def cancel_alarm(self) -> None:
        """Cancel the alarm and update timestamp"""
        self.status = AlarmStatus.CANCELLED
        self.update_timestamp()

    def is_ready_for_scheduling(self) -> bool:
        """Check if alarm is ready for scheduling (in created state)"""
        return self.state == "created"

    def is_scheduled(self) -> bool:
        """Check if alarm has been scheduled"""
        return self.state == "scheduled"

    def is_active(self) -> bool:
        """Check if alarm is currently active"""
        return self.state == "active"

    def is_completed(self) -> bool:
        """Check if alarm has completed"""
        return self.state == "completed"

    def is_cancelled(self) -> bool:
        """Check if alarm has been cancelled"""
        return self.state == "cancelled"

    def get_cooking_time_display(self) -> str:
        """Get human-readable cooking time display"""
        return f"{self.cooking_duration} minute{'s' if self.cooking_duration != 1 else ''}"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["cookingTimeDisplay"] = self.get_cooking_time_display()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
