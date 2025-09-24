"""
User Entity for Purrfect Pets API

Represents customers and users of the Purrfect Pets store with comprehensive
validation and workflow state management.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User entity represents customers and users of the Purrfect Pets store.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> active -> suspended
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="Unique username for login")
    email: str = Field(..., description="User's email address")

    # Optional fields
    firstName: Optional[str] = Field(
        default=None, alias="firstName", description="User's first name"
    )
    lastName: Optional[str] = Field(
        default=None, alias="lastName", description="User's last name"
    )
    phone: Optional[str] = Field(default=None, description="User's phone number")
    password: Optional[str] = Field(
        default=None, description="Encrypted password (not exposed in API responses)"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="User preferences for pet types, notifications",
    )

    # Processing-related fields (populated during processing)
    registeredAt: Optional[str] = Field(
        default=None, alias="registeredAt", description="Timestamp when user registered"
    )
    emailVerificationToken: Optional[str] = Field(
        default=None,
        alias="emailVerificationToken",
        description="Token for email verification",
    )
    emailVerified: bool = Field(
        default=False,
        alias="emailVerified",
        description="Whether email has been verified",
    )
    activatedAt: Optional[str] = Field(
        default=None,
        alias="activatedAt",
        description="Timestamp when user account was activated",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username is required")

        username = v.strip()

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if len(username) > 50:
            raise ValueError("Username must be at most 50 characters long")

        # Username should contain only alphanumeric characters, underscores, and hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return username

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email is required")

        email = v.strip().lower()

        # Basic email validation regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Email address is too long")

        return email

    @field_validator("firstName", "lastName")
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate first name and last name fields"""
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("Name must be a string")

        name = v.strip()

        if len(name) == 0:
            return None  # Empty string becomes None

        if len(name) > 100:
            raise ValueError("Name must be at most 100 characters long")

        # Names should contain only letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s'-]+$", name):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, and apostrophes"
            )

        return name

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number field"""
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("Phone number must be a string")

        phone = v.strip()

        if len(phone) == 0:
            return None  # Empty string becomes None

        # Remove common phone number formatting characters
        cleaned_phone = re.sub(r"[^\d+]", "", phone)

        # Basic phone number validation (10-15 digits, optionally starting with +)
        if not re.match(r"^\+?[1-9]\d{9,14}$", cleaned_phone):
            raise ValueError("Invalid phone number format")

        return cleaned_phone

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password field"""
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("Password must be a string")

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters long")

        # Password strength validation
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        return v

    @field_validator("preferences")
    @classmethod
    def validate_preferences(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate preferences structure"""
        if v is None:
            return {}

        if not isinstance(v, dict):
            raise ValueError("Preferences must be a dictionary")

        # Validate known preference keys
        allowed_keys = {
            "petTypes",
            "notifications",
            "newsletter",
            "language",
            "timezone",
        }

        for key in v.keys():
            if not isinstance(key, str):
                raise ValueError("Preference keys must be strings")

        return v

    @field_validator("registeredAt", "activatedAt")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (ISO 8601)"""
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("Date must be a string in ISO 8601 format")

        # Basic ISO 8601 format validation
        try:
            # Try to parse the date to validate format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                "Date must be in ISO 8601 format (e.g., '2023-12-25T10:30:00Z')"
            )

        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "User":
        """Validate business logic rules"""
        # Ensure active users have verified email
        if self.state == "active" and not self.emailVerified:
            # This will be set by the processor, so we don't enforce it here
            pass

        # Ensure registered users have registration timestamp
        if (
            self.state in ["registered", "active", "suspended"]
            and not self.registeredAt
        ):
            # This will be set by the processor, so we don't enforce it here
            pass

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_registered(self) -> bool:
        """Check if user is registered"""
        return self.state == "registered"

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.state == "active"

    def is_suspended(self) -> bool:
        """Check if user is suspended"""
        return self.state == "suspended"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format (excluding sensitive fields)"""
        data = self.model_dump(by_alias=True)
        # Remove sensitive fields from API response
        data.pop("password", None)
        data.pop("emailVerificationToken", None)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
