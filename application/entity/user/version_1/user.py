# entity/user/version_1/user.py

"""
User Entity for Cyoda Client Application

Manages user information and email preferences for weather notifications.
Represents user accounts with email, timezone, and notification preferences.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User entity represents a user account for weather notification system.
    
    Manages user information including email, timezone preferences, and notification settings.
    The state field manages workflow states: initial_state -> registered -> active -> suspended/deleted
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    email: str = Field(..., description="User's email address (required, unique)")
    name: Optional[str] = Field(
        default=None, description="User's display name (optional)"
    )
    timezone: str = Field(
        default="UTC", description="User's timezone for scheduling notifications"
    )
    notification_time: str = Field(
        default="08:00", description="Preferred time for daily notifications (24-hour format)"
    )
    active: bool = Field(
        default=True, description="Whether user account is active"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the user was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the user was last updated (ISO 8601 format)",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Email must be valid format")
        
        if len(v) > 255:
            raise ValueError("Email must be at most 255 characters long")
        
        return v.strip().lower()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name field"""
        if v is None:
            return v
        
        if len(v.strip()) == 0:
            return None  # Empty string becomes None
        
        if len(v) > 100:
            raise ValueError("Name must be at most 100 characters long")
        
        return v.strip()

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone field"""
        if not v or len(v.strip()) == 0:
            return "UTC"
        
        # Basic timezone validation - accept common formats
        valid_timezones = [
            "UTC", "America/Toronto", "America/Vancouver", "America/New_York",
            "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo"
        ]
        
        if v not in valid_timezones:
            # Allow any timezone format that looks reasonable
            if not re.match(r'^[A-Za-z_/]+$', v):
                raise ValueError("Timezone must be a valid timezone identifier")
        
        return v

    @field_validator("notification_time")
    @classmethod
    def validate_notification_time(cls, v: str) -> str:
        """Validate notification_time field (24-hour format)"""
        if not v or len(v.strip()) == 0:
            return "08:00"
        
        # Validate 24-hour format HH:MM
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, v.strip()):
            raise ValueError("Notification time must be in 24-hour format (HH:MM)")
        
        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "User":
        """Validate business logic rules"""
        # Business rule: Only active users receive notifications
        # This is enforced at the application level, not at the entity level
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.active = False
        self.update_timestamp()

    def activate(self) -> None:
        """Activate user account"""
        self.active = True
        self.update_timestamp()

    def is_notification_eligible(self) -> bool:
        """Check if user is eligible to receive notifications"""
        return self.active and self.state in ["active"]

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
