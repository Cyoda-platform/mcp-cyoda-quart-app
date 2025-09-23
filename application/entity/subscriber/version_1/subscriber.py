# entity/subscriber/version_1/subscriber.py

"""
Subscriber Entity for Cat Fact Subscription Application

Represents users who sign up for weekly cat fact emails.
Manages subscription status, preferences, and user information.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Subscriber(CyodaEntity):
    """
    Subscriber represents a user who has signed up for weekly cat fact emails.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> (paused/cancelled)
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Subscriber"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    email: str = Field(..., description="Email address of the subscriber")
    subscription_status: str = Field(
        default="active",
        alias="subscriptionStatus",
        description="Status of the subscription: active, paused, cancelled",
    )

    # Optional fields
    first_name: Optional[str] = Field(
        default=None, alias="firstName", description="First name of the subscriber"
    )
    last_name: Optional[str] = Field(
        default=None, alias="lastName", description="Last name of the subscriber"
    )

    # Preferences
    preferred_time: Optional[str] = Field(
        default="09:00",
        alias="preferredTime",
        description="Preferred time to receive emails (HH:MM format)",
    )
    timezone: Optional[str] = Field(default="UTC", description="Subscriber's timezone")

    # Timestamps
    subscribed_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="subscribedAt",
        description="Timestamp when the user subscribed (ISO 8601 format)",
    )
    last_email_sent: Optional[str] = Field(
        default=None,
        alias="lastEmailSent",
        description="Timestamp of the last email sent to this subscriber",
    )

    # Tracking fields
    total_emails_sent: int = Field(
        default=0,
        alias="totalEmailsSent",
        description="Total number of emails sent to this subscriber",
    )
    total_emails_opened: int = Field(
        default=0,
        alias="totalEmailsOpened",
        description="Total number of emails opened by this subscriber",
    )

    # Validation constants
    ALLOWED_SUBSCRIPTION_STATUSES: ClassVar[list[str]] = [
        "active",
        "paused",
        "cancelled",
    ]

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")

        # Basic email validation
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Email must be a valid email address")

        if len(v) > 254:  # RFC 5321 limit
            raise ValueError("Email must be at most 254 characters long")

        return v.strip().lower()

    @field_validator("subscription_status")
    @classmethod
    def validate_subscription_status(cls, v: str) -> str:
        """Validate subscription status"""
        if v not in cls.ALLOWED_SUBSCRIPTION_STATUSES:
            raise ValueError(
                f"Subscription status must be one of: {cls.ALLOWED_SUBSCRIPTION_STATUSES}"
            )
        return v

    @field_validator("preferred_time")
    @classmethod
    def validate_preferred_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate preferred time format (HH:MM)"""
        if v is None:
            return v

        if not v.strip():
            return "09:00"  # Default

        # Basic time format validation
        try:
            parts = v.split(":")
            if len(parts) != 2:
                raise ValueError("Preferred time must be in HH:MM format")

            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Preferred time must be valid (00:00 to 23:59)")

            return f"{hour:02d}:{minute:02d}"
        except (ValueError, IndexError):
            raise ValueError("Preferred time must be in HH:MM format")

    def update_email_stats(self, sent: bool = False, opened: bool = False) -> None:
        """Update email statistics"""
        if sent:
            self.total_emails_sent += 1
            self.last_email_sent = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

        if opened:
            self.total_emails_opened += 1

    def is_active(self) -> bool:
        """Check if subscriber is active"""
        return self.subscription_status == "active"

    def pause_subscription(self) -> None:
        """Pause the subscription"""
        self.subscription_status = "paused"

    def cancel_subscription(self) -> None:
        """Cancel the subscription"""
        self.subscription_status = "cancelled"

    def reactivate_subscription(self) -> None:
        """Reactivate the subscription"""
        self.subscription_status = "active"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
