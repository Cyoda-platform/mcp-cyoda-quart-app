# entity/subscriber/version_1/subscriber.py

"""
Subscriber Entity for Cyoda Client Application

Represents a user who has subscribed to receive weekly cat facts via email.
Manages subscription lifecycle from registration to unsubscription.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Subscriber(CyodaEntity):
    """
    Subscriber represents a user who has subscribed to receive weekly cat facts via email.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> pending -> active -> unsubscribed -> end
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Subscriber"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    email: str = Field(
        ..., description="Email address of the subscriber (unique, required)"
    )
    first_name: Optional[str] = Field(
        default=None,
        alias="firstName",
        description="First name of the subscriber (optional)",
    )
    last_name: Optional[str] = Field(
        default=None,
        alias="lastName",
        description="Last name of the subscriber (optional)",
    )
    subscription_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="subscriptionDate",
        description="Date and time when the user subscribed (ISO 8601 format)",
    )
    is_active: bool = Field(
        default=False,
        alias="isActive",
        description="Whether the subscription is currently active",
    )
    unsubscribe_token: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        alias="unsubscribeToken",
        description="Unique token for unsubscribing (UUID)",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email is required")

        # Basic email format validation
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")

        return v.strip().lower()

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate first name field according to criteria requirements"""
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        # Check for special characters (allow only letters, spaces, hyphens, apostrophes)
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
        if not all(c in allowed_chars for c in v):
            raise ValueError("First name cannot contain special characters")

        return v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate last name field according to criteria requirements"""
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        # Check for special characters (allow only letters, spaces, hyphens, apostrophes)
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Last name cannot contain special characters")

        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def activate_subscription(self) -> None:
        """Activate the subscription and update timestamp"""
        self.is_active = True
        self.update_timestamp()

    def deactivate_subscription(self) -> None:
        """Deactivate the subscription and update timestamp"""
        self.is_active = False
        self.update_timestamp()

    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.is_active and self.state == "active"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["id"] = self.get_id()
        data["state"] = self.state
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
