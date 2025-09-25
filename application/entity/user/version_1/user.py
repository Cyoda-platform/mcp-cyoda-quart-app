"""
User Entity for Purrfect Pets API Application

Represents a user/customer in the pet store system.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class User(CyodaEntity):
    """
    User entity represents a customer in the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> validated -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "User"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    username: str = Field(..., description="Username for the user")

    # Optional fields from Petstore API
    first_name: Optional[str] = Field(
        default=None,
        alias="firstName",
        description="First name of the user"
    )
    last_name: Optional[str] = Field(
        default=None,
        alias="lastName",
        description="Last name of the user"
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address of the user"
    )
    password: Optional[str] = Field(
        default=None,
        description="Password for the user account"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the user"
    )
    user_status: Optional[int] = Field(
        default=1,
        alias="userStatus",
        description="User status (1=active, 0=inactive)"
    )

    # Processing-related fields
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data populated during processing"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Username must be non-empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters long")
        # Basic alphanumeric check
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email"""
        if v is not None:
            if "@" not in v or "." not in v:
                raise ValueError("Invalid email format")
            if len(v) > 100:
                raise ValueError("Email must be at most 100 characters long")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate first and last names"""
        if v is not None:
            if len(v) > 50:
                raise ValueError("Name must be at most 50 characters long")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number"""
        if v is not None:
            # Remove common phone formatting characters
            cleaned = v.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace("+", "")
            if not cleaned.isdigit():
                raise ValueError("Phone number must contain only digits and common formatting characters")
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError("Phone number must be between 10 and 15 digits")
        return v

    @field_validator("user_status")
    @classmethod
    def validate_user_status(cls, v: Optional[int]) -> Optional[int]:
        """Validate user status"""
        if v is not None and v not in [0, 1]:
            raise ValueError("User status must be 0 (inactive) or 1 (active)")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def is_active(self) -> bool:
        """Check if user is active"""
        return self.user_status == 1

    def get_full_name(self) -> str:
        """Get full name of the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        # Remove password from API response for security
        if "password" in data:
            del data["password"]
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
