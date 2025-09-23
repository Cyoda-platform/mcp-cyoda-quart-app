# entity/emailnotification/version_1/email_notification.py

"""
EmailNotification Entity for Cyoda Client Application

Manages email notifications for weather updates sent to users.
Represents email notifications with delivery status and retry logic.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailNotification(CyodaEntity):
    """
    EmailNotification entity represents an email notification for weather updates.

    Manages email delivery with status tracking, retry logic, and content management.
    The state field manages workflow states: initial_state -> pending -> sending -> sent/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailNotification"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    user_id: str = Field(..., description="Reference to User entity (required)")
    weather_data_id: str = Field(
        ..., description="Reference to WeatherData entity (required)"
    )
    recipient_email: str = Field(
        ..., description="Email address to send notification (required)"
    )
    subject: str = Field(..., description="Email subject line (required)")
    content: str = Field(..., description="Email body content (required)")
    sent_timestamp: Optional[str] = Field(
        default=None, description="When email was sent (nullable)"
    )
    delivery_status: str = Field(
        default="pending", description="Email delivery status (pending, sent, failed)"
    )
    retry_count: int = Field(
        default=0, description="Number of send attempts (default: 0)"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the notification was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the notification was last updated (ISO 8601 format)",
    )

    # Business constants
    MAX_RETRY_ATTEMPTS: ClassVar[int] = 3
    ALLOWED_DELIVERY_STATUSES: ClassVar[List[str]] = [
        "pending",
        "sending",
        "sent",
        "failed",
    ]

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID must be non-empty")

        if len(v) > 255:
            raise ValueError("User ID must be at most 255 characters long")

        return v.strip()

    @field_validator("weather_data_id")
    @classmethod
    def validate_weather_data_id(cls, v: str) -> str:
        """Validate weather_data_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Weather Data ID must be non-empty")

        if len(v) > 255:
            raise ValueError("Weather Data ID must be at most 255 characters long")

        return v.strip()

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Validate recipient_email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Recipient email must be non-empty")

        # Basic email format validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Recipient email must be valid format")

        if len(v) > 255:
            raise ValueError("Recipient email must be at most 255 characters long")

        return v.strip().lower()

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Validate subject field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Subject must be non-empty")

        if len(v) > 255:
            raise ValueError("Subject must be at most 255 characters long")

        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Content must be non-empty")

        if len(v) > 10000:  # Allow longer content for email body
            raise ValueError("Content must be at most 10000 characters long")

        return v.strip()

    @field_validator("sent_timestamp")
    @classmethod
    def validate_sent_timestamp(cls, v: Optional[str]) -> Optional[str]:
        """Validate sent_timestamp field (ISO 8601 format)"""
        if v is None:
            return v

        if len(v.strip()) == 0:
            return None

        # Try to parse the timestamp to validate format
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Sent timestamp must be in ISO 8601 format")

        return v.strip()

    @field_validator("delivery_status")
    @classmethod
    def validate_delivery_status(cls, v: str) -> str:
        """Validate delivery_status field"""
        if not v or len(v.strip()) == 0:
            return "pending"

        v_clean = v.strip().lower()
        if v_clean not in cls.ALLOWED_DELIVERY_STATUSES:
            raise ValueError(
                f"Delivery status must be one of: {cls.ALLOWED_DELIVERY_STATUSES}"
            )

        return v_clean

    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(cls, v: int) -> int:
        """Validate retry_count field"""
        if v < 0:
            raise ValueError("Retry count must be non-negative")

        if v > cls.MAX_RETRY_ATTEMPTS:
            raise ValueError(f"Retry count must not exceed {cls.MAX_RETRY_ATTEMPTS}")

        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "EmailNotification":
        """Validate business logic rules"""
        # Business rule: Maximum 3 retry attempts for failed emails
        if self.retry_count > self.MAX_RETRY_ATTEMPTS:
            raise ValueError(
                f"Maximum retry attempts ({self.MAX_RETRY_ATTEMPTS}) exceeded"
            )

        # Business rule: sent_timestamp should be set when status is 'sent'
        if self.delivery_status == "sent" and self.sent_timestamp is None:
            # Auto-set sent_timestamp if not provided
            self.sent_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_as_sent(self) -> None:
        """Mark notification as successfully sent"""
        self.delivery_status = "sent"
        self.sent_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def mark_as_failed(self) -> None:
        """Mark notification as failed"""
        self.delivery_status = "failed"
        self.update_timestamp()

    def increment_retry_count(self) -> None:
        """Increment retry count"""
        if self.retry_count < self.MAX_RETRY_ATTEMPTS:
            self.retry_count += 1
            self.update_timestamp()

    def can_retry(self) -> bool:
        """Check if notification can be retried"""
        return (
            self.delivery_status == "failed"
            and self.retry_count < self.MAX_RETRY_ATTEMPTS
        )

    def is_delivery_complete(self) -> bool:
        """Check if delivery is complete (sent or permanently failed)"""
        return self.delivery_status == "sent" or (
            self.delivery_status == "failed"
            and self.retry_count >= self.MAX_RETRY_ATTEMPTS
        )

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
