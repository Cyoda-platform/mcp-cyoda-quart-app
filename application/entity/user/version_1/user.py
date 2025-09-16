"""
User Entity for Purrfect Pets API

Represents users of the Purrfect Pets system (customers, staff, admins).
The User entity uses workflow states managed by the system.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User represents users of the Purrfect Pets system (customers, staff, admins).
    
    The User entity uses `userStatus` semantically as its state, which will be managed 
    by the system as `entity.meta.state`. The possible states are:
    - `active`: User account is active
    - `inactive`: User account is inactive
    - `suspended`: User account is suspended
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    username: str = Field(..., description="Unique username")
    firstName: str = Field(..., alias="firstName", description="First name of the user")
    lastName: str = Field(..., alias="lastName", description="Last name of the user")
    email: str = Field(..., description="Email address of the user")
    phone: str = Field(..., description="Phone number of the user")
    
    # Optional fields
    role: str = Field(default="CUSTOMER", description="Role of the user (CUSTOMER, STAFF, ADMIN)")
    registrationDate: Optional[str] = Field(
        default=None, 
        alias="registrationDate", 
        description="Date when user registered"
    )
    lastLoginDate: Optional[str] = Field(
        default=None, 
        alias="lastLoginDate", 
        description="Last login date"
    )
    
    # Processing-related fields (populated during processing)
    deactivatedDate: Optional[str] = Field(
        default=None, 
        alias="deactivatedDate", 
        description="Date when user was deactivated"
    )
    deactivatedBy: Optional[str] = Field(
        default=None, 
        alias="deactivatedBy", 
        description="Who deactivated the user"
    )
    reactivatedDate: Optional[str] = Field(
        default=None, 
        alias="reactivatedDate", 
        description="Date when user was reactivated"
    )
    suspendedDate: Optional[str] = Field(
        default=None, 
        alias="suspendedDate", 
        description="Date when user was suspended"
    )
    suspendedBy: Optional[str] = Field(
        default=None, 
        alias="suspendedBy", 
        description="Who suspended the user"
    )
    suspensionReason: Optional[str] = Field(
        default=None, 
        alias="suspensionReason", 
        description="Reason for suspension"
    )
    suspensionExpiry: Optional[str] = Field(
        default=None, 
        alias="suspensionExpiry", 
        description="When suspension expires"
    )
    unsuspendedDate: Optional[str] = Field(
        default=None, 
        alias="unsuspendedDate", 
        description="Date when user was unsuspended"
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
        return v.strip().lower()

    @field_validator("firstName")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate firstName field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v) > 50:
            raise ValueError("First name must be at most 50 characters long")
        return v.strip()

    @field_validator("lastName")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate lastName field"""
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
        if "@" not in v:
            raise ValueError("Email must be valid")
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Phone must be non-empty")
        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role field"""
        allowed_roles = ["CUSTOMER", "STAFF", "ADMIN"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {allowed_roles}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "User":
        """Validate business logic rules"""
        # Additional business validation can be added here
        return self

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

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
