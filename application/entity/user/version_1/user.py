# entity/user/version_1/user.py

"""
User Entity for Cyoda Client Application

Represents system users with authentication credentials and role assignments
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User represents system users with authentication credentials and role assignments.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending -> active -> suspended/inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="Unique identifier for login")
    email: str = Field(..., description="User email address (unique)")
    password_hash: str = Field(..., description="Encrypted password")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")

    # Optional fields
    is_active: Optional[bool] = Field(default=True, description="Account status flag")
    role_ids: Optional[List[str]] = Field(
        default_factory=list, description="Array of assigned role IDs"
    )
    last_login: Optional[str] = Field(
        default=None, description="Last login timestamp (ISO 8601 format)"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the entity was last updated (ISO 8601 format)",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username must be non-empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long")
        # Basic alphanumeric validation
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v.strip().lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        if "@" not in v or "." not in v:
            raise ValueError("Email must be a valid email address")
        if len(v) > 255:
            raise ValueError("Email must be at most 255 characters long")
        return v.strip().lower()

    @field_validator("password_hash")
    @classmethod
    def validate_password_hash(cls, v: str) -> str:
        """Validate password hash field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Password hash must be non-empty")
        if len(v) < 32:  # Minimum hash length
            raise ValueError("Password hash appears to be invalid")
        return v.strip()

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate first name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v) > 100:
            raise ValueError("First name must be at most 100 characters long")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate last name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Last name must be non-empty")
        if len(v) > 100:
            raise ValueError("Last name must be at most 100 characters long")
        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "User":
        """Validate business logic rules according to functional requirements"""
        # Additional business logic validation can be added here
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add_role(self, role_id: str) -> None:
        """Add a role to the user"""
        if self.role_ids is None:
            self.role_ids = []
        if role_id not in self.role_ids:
            self.role_ids.append(role_id)
            self.update_timestamp()

    def remove_role(self, role_id: str) -> None:
        """Remove a role from the user"""
        if self.role_ids and role_id in self.role_ids:
            self.role_ids.remove(role_id)
            self.update_timestamp()

    def has_role(self, role_id: str) -> bool:
        """Check if user has a specific role"""
        return self.role_ids is not None and role_id in self.role_ids

    def set_last_login(self) -> None:
        """Update last login timestamp to current time"""
        self.last_login = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def is_account_active(self) -> bool:
        """Check if user account is active"""
        return self.is_active is True and self.state == "active"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format (excluding sensitive data)"""
        data = self.model_dump(by_alias=True)
        # Remove sensitive information from API response
        data.pop("password_hash", None)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
