"""
User Entity for Purrfect Pets Application

Represents a user/customer of the pet store with all required attributes
as specified in functional requirements.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User entity represents a user/customer of the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> verified -> active -> suspended/deactivated -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    username: str = Field(..., description="Username for login")
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Encrypted password")

    # Personal information
    first_name: Optional[str] = Field(None, alias="firstName", description="First name of the user")
    last_name: Optional[str] = Field(None, alias="lastName", description="Last name of the user")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Address information
    address: Optional[str] = Field(None, description="Primary address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    zip_code: Optional[str] = Field(None, alias="zipCode", description="ZIP/Postal code")
    country: Optional[str] = Field(None, description="Country")
    
    # Additional information
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth", description="Date of birth")
    preferred_pet_type: Optional[str] = Field(None, alias="preferredPetType", description="Preferred type of pet")
    
    # Status flags
    is_active: Optional[bool] = Field(default=True, alias="isActive", description="Whether the user account is active")
    email_verified: Optional[bool] = Field(default=False, alias="emailVerified", description="Whether email is verified")

    # Audit timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="When the user account was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="When the user account was last updated"
    )
    last_login_at: Optional[str] = Field(
        default=None,
        alias="lastLoginAt",
        description="When the user last logged in"
    )

    # Validation constants
    EMAIL_REGEX: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX: ClassVar[str] = r'^\+?[\d\s\-\(\)]{10,20}$'
    USERNAME_REGEX: ClassVar[str] = r'^[a-zA-Z0-9_]{3,30}$'

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username is required")
        v = v.strip()
        if not re.match(cls.USERNAME_REGEX, v):
            raise ValueError("Username must be 3-30 characters long and contain only letters, numbers, and underscores")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email is required")
        v = v.strip().lower()
        if not re.match(cls.EMAIL_REGEX, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password"""
        if not v or len(v) == 0:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters long")
        return v

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate first name"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 50:
                raise ValueError("First name must be at most 50 characters long")
            return v
        return v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate last name"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 50:
                raise ValueError("Last name must be at most 50 characters long")
            return v
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(cls.PHONE_REGEX, v):
                raise ValueError("Invalid phone number format")
            return v
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate ZIP code"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 20:
                raise ValueError("ZIP code must be at most 20 characters long")
            return v
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_last_login(self) -> None:
        """Update the last_login_at timestamp to current time"""
        self.last_login_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_registered(self) -> bool:
        """Check if user is registered"""
        return self.state == "registered"

    def is_verified(self) -> bool:
        """Check if user is verified"""
        return self.state == "verified"

    def is_user_active(self) -> bool:
        """Check if user is active"""
        return self.state == "active"

    def is_suspended(self) -> bool:
        """Check if user is suspended"""
        return self.state == "suspended"

    def is_deactivated(self) -> bool:
        """Check if user is deactivated"""
        return self.state == "deactivated"

    def is_archived(self) -> bool:
        """Check if user is archived"""
        return self.state == "archived"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format (excluding password)"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        # Remove password from API response for security
        data.pop("password", None)
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
