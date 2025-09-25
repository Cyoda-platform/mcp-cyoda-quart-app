# entity/email_notification/version_1/email_notification.py

"""
EmailNotification Entity for Pet Store Performance Analysis System

Represents an email notification for sending performance reports to the sales team
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailNotification(CyodaEntity):
    """
    EmailNotification represents an email notification for sending performance
    reports to the sales team, specifically to victoria.sagdieva@cyoda.com.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> sent -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailNotification"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core email fields
    recipient_email: str = Field(
        ..., alias="recipientEmail", description="Email address of the recipient"
    )
    subject: str = Field(..., description="Email subject line")
    content: Optional[str] = Field(default=None, description="Email body content")

    # Email metadata
    sender_email: Optional[str] = Field(
        default="noreply@cyoda.com",
        alias="senderEmail",
        description="Email address of the sender",
    )
    email_type: str = Field(
        default="REPORT_NOTIFICATION",
        alias="emailType",
        description="Type of email notification",
    )
    priority: str = Field(
        default="NORMAL", description="Email priority: LOW, NORMAL, HIGH, URGENT"
    )

    # Report reference
    report_id: Optional[str] = Field(
        default=None, alias="reportId", description="ID of the associated report"
    )
    report_title: Optional[str] = Field(
        default=None, alias="reportTitle", description="Title of the associated report"
    )

    # Email status and tracking
    status: str = Field(
        default="PENDING", description="Email status: PENDING, SENT, FAILED, DELIVERED"
    )
    delivery_attempts: int = Field(
        default=0,
        alias="deliveryAttempts",
        description="Number of delivery attempts made",
    )
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if delivery failed",
    )

    # Timestamps
    scheduled_at: Optional[str] = Field(
        default=None,
        alias="scheduledAt",
        description="When the email is scheduled to be sent",
    )
    sent_at: Optional[str] = Field(
        default=None, alias="sentAt", description="Timestamp when email was sent"
    )
    delivered_at: Optional[str] = Field(
        default=None,
        alias="deliveredAt",
        description="Timestamp when email was delivered",
    )

    # Validation constants
    ALLOWED_EMAIL_TYPES: ClassVar[List[str]] = [
        "REPORT_NOTIFICATION",
        "ALERT",
        "SUMMARY",
        "WEEKLY_REPORT",
        "MONTHLY_REPORT",
    ]

    ALLOWED_PRIORITIES: ClassVar[List[str]] = ["LOW", "NORMAL", "HIGH", "URGENT"]

    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "PENDING",
        "SENT",
        "FAILED",
        "DELIVERED",
        "CANCELLED",
    ]

    @field_validator("recipient_email", "sender_email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate email address format"""
        if v is not None:
            if not v or "@" not in v or "." not in v.split("@")[-1]:
                raise ValueError(f"Invalid email address format: {v}")
            if len(v) > 254:  # RFC 5321 limit
                raise ValueError("Email address too long")
        return v

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Validate email subject field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email subject must be non-empty")
        if len(v) > 200:
            raise ValueError("Email subject must be at most 200 characters long")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate email content field"""
        if v is not None and len(v) > 100000:  # 100KB limit
            raise ValueError("Email content must be at most 100,000 characters long")
        return v

    @field_validator("email_type")
    @classmethod
    def validate_email_type(cls, v: str) -> str:
        """Validate email type field"""
        if v not in cls.ALLOWED_EMAIL_TYPES:
            raise ValueError(f"Email type must be one of: {cls.ALLOWED_EMAIL_TYPES}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority field"""
        if v not in cls.ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of: {cls.ALLOWED_PRIORITIES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("delivery_attempts")
    @classmethod
    def validate_delivery_attempts(cls, v: int) -> int:
        """Validate delivery attempts field"""
        if v < 0:
            raise ValueError("Delivery attempts must be non-negative")
        if v > 10:
            raise ValueError("Delivery attempts cannot exceed 10")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "EmailNotification":
        """Validate business logic rules"""
        # Validate status consistency with timestamps
        if self.status == "SENT" and not self.sent_at:
            raise ValueError("If status is SENT, sent_at timestamp must be set")

        if self.status == "DELIVERED" and not self.delivered_at:
            raise ValueError(
                "If status is DELIVERED, delivered_at timestamp must be set"
            )

        if self.status == "FAILED" and self.delivery_attempts == 0:
            raise ValueError(
                "If status is FAILED, delivery_attempts must be greater than 0"
            )

        # Validate timestamp order
        if self.sent_at and self.delivered_at:
            try:
                sent_time = datetime.fromisoformat(self.sent_at.replace("Z", "+00:00"))
                delivered_time = datetime.fromisoformat(
                    self.delivered_at.replace("Z", "+00:00")
                )
                if sent_time > delivered_time:
                    raise ValueError("sent_at must be before delivered_at")
            except ValueError as e:
                if "sent_at must be before delivered_at" in str(e):
                    raise
                raise ValueError("Invalid timestamp format")

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_as_sent(self) -> None:
        """Mark email as sent"""
        self.status = "SENT"
        self.sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.delivery_attempts += 1
        self.update_timestamp()

    def mark_as_delivered(self) -> None:
        """Mark email as delivered"""
        self.status = "DELIVERED"
        self.delivered_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def mark_as_failed(self, error_message: str) -> None:
        """Mark email as failed with error message"""
        self.status = "FAILED"
        self.error_message = error_message
        self.delivery_attempts += 1
        self.update_timestamp()

    def schedule_email(self, scheduled_time: str) -> None:
        """Schedule email for future delivery"""
        self.scheduled_at = scheduled_time
        self.update_timestamp()

    def is_ready_to_send(self) -> bool:
        """Check if email is ready to be sent"""
        return (
            self.status == "PENDING"
            and self.content is not None
            and len(self.content.strip()) > 0
            and self.delivery_attempts < 3  # Max retry limit
        )

    def can_retry(self) -> bool:
        """Check if email can be retried after failure"""
        return self.status == "FAILED" and self.delivery_attempts < 3

    def get_email_summary(self) -> Dict[str, Any]:
        """Get a summary of the email for API responses"""
        return {
            "recipient": self.recipient_email,
            "subject": self.subject,
            "status": self.status,
            "email_type": self.email_type,
            "priority": self.priority,
            "delivery_attempts": self.delivery_attempts,
            "sent_at": self.sent_at,
            "report_id": self.report_id,
        }

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
