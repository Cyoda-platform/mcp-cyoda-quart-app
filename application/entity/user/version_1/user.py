"""
User Entity for Purrfect Pets API

Represents a user (customer, admin, staff) as specified in the functional requirements.
"""

import re
from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User entity representing system users.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive/suspended
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="Username", max_length=50)
    first_name: str = Field(..., description="First name", max_length=50)
    last_name: str = Field(..., description="Last name", max_length=50)
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Hashed password", min_length=8)
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)
    address: Optional[str] = Field(None, description="User address", max_length=200)
    user_type: str = Field(..., description="User type: customer, admin, staff")

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the user was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the user was last updated (ISO 8601 format)",
    )

    # Valid user types
    VALID_USER_TYPES: ClassVar[list[str]] = ["customer", "admin", "staff"]

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username must be non-empty")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long")
        return v.strip()

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate first_name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v) > 50:
            raise ValueError("First name must be at most 50 characters long")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate last_name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Last name must be non-empty")
        if len(v) > 50:
            raise ValueError("Last name must be at most 50 characters long")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Email must be in valid format")

        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password field"""
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 20:
            raise ValueError("Phone number must be at most 20 characters long")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate address field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 200:
            raise ValueError("Address must be at most 200 characters long")
        return v.strip()

    @field_validator("user_type")
    @classmethod
    def validate_user_type(cls, v: str) -> str:
        """Validate user_type field"""
        if v not in cls.VALID_USER_TYPES:
            raise ValueError(f"User type must be one of: {cls.VALID_USER_TYPES}")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.state == "active"

    def is_inactive(self) -> bool:
        """Check if user is inactive"""
        return self.state == "inactive"

    def is_suspended(self) -> bool:
        """Check if user is suspended"""
        return self.state == "suspended"

    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
