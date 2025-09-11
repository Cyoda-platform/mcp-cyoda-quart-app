"""
User Entity for Purrfect Pets API

Represents users of the system (customers and staff) as specified
in functional requirements.
"""

from datetime import datetime
from enum import Enum
from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class UserRole(str, Enum):
    """User role enumeration"""

    CUSTOMER = "CUSTOMER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class Address(CyodaEntity):
    """Address reference for User entity"""

    ENTITY_NAME: ClassVar[str] = "Address"
    ENTITY_VERSION: ClassVar[int] = 1

    id: Optional[int] = Field(None, description="Address ID")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    zip_code: Optional[str] = Field(
        None, alias="zipCode", description="ZIP or postal code"
    )
    country: Optional[str] = Field(None, description="Country name")


class User(CyodaEntity):
    """
    User entity represents users of the system.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the user")
    username: str = Field(..., description="Username for login (required, unique)")
    email: str = Field(..., description="Email address (required, unique)")
    password: str = Field(..., description="Encrypted password (required)")

    # Optional fields
    first_name: Optional[str] = Field(
        None, alias="firstName", description="First name of the user"
    )
    last_name: Optional[str] = Field(
        None, alias="lastName", description="Last name of the user"
    )
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[Address] = Field(None, description="User's address")
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="Role of the user (CUSTOMER, STAFF, ADMIN)",
    )
    registration_date: Optional[datetime] = Field(
        None, alias="registrationDate", description="When the user registered"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username is required and cannot be empty")
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email is required and cannot be empty")
        # Basic email validation
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password field"""
        if not v or len(v) == 0:
            raise ValueError("Password is required and cannot be empty")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.state == "active"

    def is_suspended(self) -> bool:
        """Check if user is suspended"""
        return self.state == "suspended"

    def is_pending_verification(self) -> bool:
        """Check if user is pending verification"""
        return self.state == "pending_verification"

    def get_status(self) -> str:
        """Get user status based on state"""
        state_mapping = {
            "active": "ACTIVE",
            "inactive": "INACTIVE",
            "suspended": "SUSPENDED",
            "pending_verification": "PENDING_VERIFICATION",
        }
        return state_mapping.get(self.state, "UNKNOWN")
