# entity/subscriber/version_1/subscriber.py

"""
Subscriber Entity for Cat Fact Subscription Application

Represents a user who has subscribed to receive weekly cat facts via email.
Manages subscription status, email preferences, and subscription metadata.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Subscriber(CyodaEntity):
    """
    Subscriber entity represents a user who has subscribed to receive weekly cat facts.
    
    Manages email address, subscription status, and subscription preferences.
    The state field manages workflow states: initial_state -> active -> (optionally) unsubscribed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Subscriber"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    email: str = Field(..., description="Email address of the subscriber")
    
    # Optional fields
    first_name: Optional[str] = Field(
        default=None,
        description="First name of the subscriber"
    )
    last_name: Optional[str] = Field(
        default=None,
        description="Last name of the subscriber"
    )
    
    # Subscription preferences
    is_active: bool = Field(
        default=True,
        alias="isActive",
        description="Whether the subscription is active"
    )
    
    # Timestamps
    subscribed_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="subscribedAt",
        description="Timestamp when the user subscribed (ISO 8601 format)"
    )
    unsubscribed_at: Optional[str] = Field(
        default=None,
        alias="unsubscribedAt",
        description="Timestamp when the user unsubscribed (ISO 8601 format)"
    )
    
    # Delivery tracking
    last_email_sent_at: Optional[str] = Field(
        default=None,
        alias="lastEmailSentAt",
        description="Timestamp of the last email sent to this subscriber"
    )
    total_emails_sent: int = Field(
        default=0,
        alias="totalEmailsSent",
        description="Total number of emails sent to this subscriber"
    )
    
    # Metadata
    subscription_source: Optional[str] = Field(
        default="web",
        alias="subscriptionSource",
        description="Source of the subscription (web, api, etc.)"
    )

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

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        """Validate name fields"""
        if v is None:
            return v
        
        v = v.strip()
        if len(v) == 0:
            return None
        
        if len(v) > 100:
            raise ValueError("Name must be at most 100 characters long")
        
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        # This method is inherited from CyodaEntity but we can override if needed
        pass

    def unsubscribe(self) -> None:
        """Mark subscriber as unsubscribed"""
        self.is_active = False
        self.unsubscribed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def resubscribe(self) -> None:
        """Reactivate subscription"""
        self.is_active = True
        self.unsubscribed_at = None

    def record_email_sent(self) -> None:
        """Record that an email was sent to this subscriber"""
        self.last_email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.total_emails_sent += 1

    def get_display_name(self) -> str:
        """Get display name for the subscriber"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.email

    def is_eligible_for_email(self) -> bool:
        """Check if subscriber is eligible to receive emails"""
        return self.is_active and self.state != "unsubscribed"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
