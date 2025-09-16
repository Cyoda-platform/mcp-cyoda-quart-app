# entity/user/version_1/user.py

"""
User for Cyoda Client Application

Represents a user of the Egg Alarm application with account management
and preferences as specified in functional requirements.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User represents a user of the Egg Alarm application.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: REGISTERED -> ACTIVE -> SUSPENDED/DELETED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="User's chosen username")
    email: str = Field(..., description="User's email address")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="When the user account was created (ISO 8601 format)",
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="User preferences for default alarm settings",
    )

    # Email validation regex
    EMAIL_REGEX: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username must be non-empty")
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v.strip()) > 50:
            raise ValueError("Username must be at most 50 characters long")
        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        email = v.strip().lower()
        if not re.match(cls.EMAIL_REGEX, email):
            raise ValueError("Email must be a valid email address")
        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Email must be at most 254 characters long")
        return email

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and set default preferences if needed"""
        if v is None:
            v = {}
        
        # Set default preferences if not provided
        defaults = {
            "defaultEggType": "MEDIUM_BOILED",
            "notificationSound": "classic",
            "autoStart": False,
            "reminderMinutes": 1,
        }
        
        for key, default_value in defaults.items():
            if key not in v:
                v[key] = default_value
        
        # Validate specific preference values
        if "defaultEggType" in v and v["defaultEggType"] not in ["SOFT_BOILED", "MEDIUM_BOILED", "HARD_BOILED"]:
            raise ValueError("defaultEggType must be one of: SOFT_BOILED, MEDIUM_BOILED, HARD_BOILED")
        
        if "notificationSound" in v and not isinstance(v["notificationSound"], str):
            raise ValueError("notificationSound must be a string")
        
        if "autoStart" in v and not isinstance(v["autoStart"], bool):
            raise ValueError("autoStart must be a boolean")
        
        if "reminderMinutes" in v and (not isinstance(v["reminderMinutes"], int) or v["reminderMinutes"] < 0):
            raise ValueError("reminderMinutes must be a non-negative integer")
        
        return v

    def update_timestamp(self) -> None:
        """Update the createdAt timestamp to current time"""
        self.createdAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        """Update user preferences"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences.update(new_preferences)
        self.update_timestamp()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value"""
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a specific preference value"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
        self.update_timestamp()

    def get_default_egg_type(self) -> str:
        """Get the user's default egg type preference"""
        return self.get_preference("defaultEggType", "MEDIUM_BOILED")

    def is_email_verified(self) -> bool:
        """Check if email is verified (placeholder for actual verification logic)"""
        # In a real implementation, this would check against a verification service
        # For now, we'll assume all emails are verified for testing purposes
        return True

    def is_admin_user(self) -> bool:
        """Check if user is an admin (placeholder for actual admin logic)"""
        # In a real implementation, this would check against admin roles/permissions
        # For now, we'll check if username contains 'admin'
        return "admin" in self.username.lower()

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        # Remove sensitive information if needed
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
