# entity/user/version_1/user.py

"""
User Entity for Cyoda Client Application

Represents a customer in the Purrfect Pets store.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User represents a customer in the Purrfect Pets store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="Email address")
    
    # Optional fields
    first_name: Optional[str] = Field(
        default=None,
        alias="firstName",
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        alias="lastName",
        description="User's last name"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number"
    )
    address: Optional[str] = Field(
        default=None,
        description="Physical address"
    )
    
    # Processing-related fields (populated during processing)
    registered_date: Optional[str] = Field(
        default=None,
        alias="registeredDate",
        description="Date when user was registered"
    )
    activated_date: Optional[str] = Field(
        default=None,
        alias="activatedDate",
        description="Date when user was activated"
    )
    deactivated_date: Optional[str] = Field(
        default=None,
        alias="deactivatedDate",
        description="Date when user was deactivated"
    )
    last_updated: Optional[str] = Field(
        default=None,
        alias="lastUpdated",
        description="Last update timestamp"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username must be non-empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long")
        # Basic alphanumeric validation
        username = v.strip()
        if not username.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return username

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        email = v.strip().lower()
        # Basic email validation
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Email must be a valid email address")
        if len(email) > 254:
            raise ValueError("Email must be at most 254 characters long")
        return email

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate first_name field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 50:
            raise ValueError("First name must be at most 50 characters long")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate last_name field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 50:
            raise ValueError("Last name must be at most 50 characters long")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        phone = v.strip()
        if len(phone) > 20:
            raise ValueError("Phone number must be at most 20 characters long")
        return phone

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

    def update_timestamp(self) -> None:
        """Update the last_updated timestamp to current time"""
        self.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_registered_date(self) -> None:
        """Set registered date and update timestamp"""
        self.registered_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_activated_date(self) -> None:
        """Set activated date and update timestamp"""
        self.activated_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_deactivated_date(self) -> None:
        """Set deactivated date and update timestamp"""
        self.deactivated_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def clear_deactivated_date(self) -> None:
        """Clear deactivated date and update timestamp"""
        self.deactivated_date = None
        self.update_timestamp()

    def is_registered(self) -> bool:
        """Check if user is registered"""
        return self.state == "registered"

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.state == "active"

    def is_inactive(self) -> bool:
        """Check if user is inactive"""
        return self.state == "inactive"

    def get_full_name(self) -> str:
        """Get user's full name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["meta"] = {"state": self.state}
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
