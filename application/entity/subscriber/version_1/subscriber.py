# entity/subscriber/version_1/subscriber.py

"""
Subscriber Entity for Cat Facts Subscription System

Represents a user who has subscribed to receive weekly cat facts via email.
Manages subscription status, email validation, and user preferences.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, EmailStr

from common.entity.cyoda_entity import CyodaEntity


class Subscriber(CyodaEntity):
    """
    Subscriber entity represents a user who has subscribed to receive weekly cat facts.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> subscribed -> confirmed -> active
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Subscriber"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    email: EmailStr = Field(..., description="Subscriber's email address")
    subscription_status: str = Field(
        default="pending",
        description="Current subscription status: pending, confirmed, active, paused, unsubscribed"
    )
    
    # Optional fields
    first_name: Optional[str] = Field(
        default=None,
        description="Subscriber's first name"
    )
    last_name: Optional[str] = Field(
        default=None,
        description="Subscriber's last name"
    )
    
    # Subscription preferences
    preferred_frequency: str = Field(
        default="weekly",
        description="Preferred email frequency: weekly, daily, monthly"
    )
    
    # Timestamps
    subscribed_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when user subscribed (ISO 8601 format)"
    )
    confirmed_at: Optional[str] = Field(
        default=None,
        description="Timestamp when subscription was confirmed (ISO 8601 format)"
    )
    last_email_sent_at: Optional[str] = Field(
        default=None,
        description="Timestamp of last email sent to subscriber (ISO 8601 format)"
    )
    
    # Engagement tracking
    total_emails_sent: int = Field(
        default=0,
        description="Total number of emails sent to this subscriber"
    )
    total_emails_opened: int = Field(
        default=0,
        description="Total number of emails opened by this subscriber"
    )
    total_emails_clicked: int = Field(
        default=0,
        description="Total number of emails clicked by this subscriber"
    )
    
    # Validation constants
    ALLOWED_STATUSES: ClassVar[list[str]] = [
        "pending",
        "confirmed", 
        "active",
        "paused",
        "unsubscribed"
    ]
    
    ALLOWED_FREQUENCIES: ClassVar[list[str]] = [
        "daily",
        "weekly", 
        "monthly"
    ]

    @field_validator("subscription_status")
    @classmethod
    def validate_subscription_status(cls, v: str) -> str:
        """Validate subscription status field"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Subscription status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("preferred_frequency")
    @classmethod
    def validate_preferred_frequency(cls, v: str) -> str:
        """Validate preferred frequency field"""
        if v not in cls.ALLOWED_FREQUENCIES:
            raise ValueError(f"Preferred frequency must be one of: {cls.ALLOWED_FREQUENCIES}")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate name fields"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 100:
                raise ValueError("Name must be at most 100 characters long")
        return v

    def confirm_subscription(self) -> None:
        """Mark subscription as confirmed and update timestamp"""
        self.subscription_status = "confirmed"
        self.confirmed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def activate_subscription(self) -> None:
        """Activate the subscription"""
        self.subscription_status = "active"
        self.update_timestamp()

    def pause_subscription(self) -> None:
        """Pause the subscription"""
        self.subscription_status = "paused"
        self.update_timestamp()

    def unsubscribe(self) -> None:
        """Unsubscribe the user"""
        self.subscription_status = "unsubscribed"
        self.update_timestamp()

    def record_email_sent(self) -> None:
        """Record that an email was sent to this subscriber"""
        self.total_emails_sent += 1
        self.last_email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def record_email_opened(self) -> None:
        """Record that subscriber opened an email"""
        self.total_emails_opened += 1
        self.update_timestamp()

    def record_email_clicked(self) -> None:
        """Record that subscriber clicked a link in an email"""
        self.total_emails_clicked += 1
        self.update_timestamp()

    def get_engagement_rate(self) -> float:
        """Calculate email engagement rate (opens/sent)"""
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_emails_opened / self.total_emails_sent

    def get_click_through_rate(self) -> float:
        """Calculate click-through rate (clicks/opens)"""
        if self.total_emails_opened == 0:
            return 0.0
        return self.total_emails_clicked / self.total_emails_opened

    def is_active_subscriber(self) -> bool:
        """Check if subscriber is active and can receive emails"""
        return self.subscription_status in ["confirmed", "active"]

    def get_display_name(self) -> str:
        """Get display name for the subscriber"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return str(self.email)

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["display_name"] = self.get_display_name()
        data["engagement_rate"] = self.get_engagement_rate()
        data["click_through_rate"] = self.get_click_through_rate()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
