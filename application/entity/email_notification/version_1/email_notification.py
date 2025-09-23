# entity/email_notification/version_1/email_notification.py

"""
EmailNotification Entity for Product Performance Analysis System

Represents email notifications for weekly performance reports sent to the sales team
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailNotification(CyodaEntity):
    """
    EmailNotification represents email dispatch tracking for performance reports.

    Tracks email notifications sent to the sales team with report attachments
    and delivery status as specified in functional requirements.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailNotification"
    ENTITY_VERSION: ClassVar[int] = 1

    # Email metadata
    subject: str = Field(..., description="Email subject line")
    recipient_email: str = Field(
        ..., alias="recipientEmail", description="Primary recipient email address"
    )
    cc_recipients: List[str] = Field(
        default_factory=list,
        alias="ccRecipients",
        description="List of CC recipient email addresses",
    )
    bcc_recipients: List[str] = Field(
        default_factory=list,
        alias="bccRecipients",
        description="List of BCC recipient email addresses",
    )

    # Email content
    email_body: str = Field(
        ..., alias="emailBody", description="Main body content of the email"
    )
    email_format: str = Field(
        default="html",
        alias="emailFormat",
        description="Format of the email content (html, text)",
    )

    # Report attachment information
    report_id: Optional[str] = Field(
        default=None,
        alias="reportId",
        description="ID of the associated PerformanceReport entity",
    )
    attachment_file_path: Optional[str] = Field(
        default=None,
        alias="attachmentFilePath",
        description="Path to the report attachment file",
    )
    attachment_file_name: Optional[str] = Field(
        default=None,
        alias="attachmentFileName",
        description="Name of the attachment file",
    )
    attachment_file_size: Optional[int] = Field(
        default=None,
        alias="attachmentFileSize",
        description="Size of the attachment file in bytes",
    )

    # Delivery tracking
    send_status: str = Field(
        default="pending",
        alias="sendStatus",
        description="Status of email delivery (pending, sent, failed, bounced)",
    )
    scheduled_send_time: Optional[str] = Field(
        default=None,
        alias="scheduledSendTime",
        description="Scheduled time for email delivery (ISO 8601)",
    )
    actual_send_time: Optional[str] = Field(
        default=None,
        alias="actualSendTime",
        description="Actual time when email was sent (ISO 8601)",
    )
    delivery_confirmation_time: Optional[str] = Field(
        default=None,
        alias="deliveryConfirmationTime",
        description="Time when delivery was confirmed (ISO 8601)",
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if email delivery failed",
    )
    retry_count: int = Field(
        default=0, alias="retryCount", description="Number of delivery retry attempts"
    )
    max_retries: int = Field(
        default=3, alias="maxRetries", description="Maximum number of retry attempts"
    )

    # Email service configuration
    email_provider: str = Field(
        default="smtp",
        alias="emailProvider",
        description="Email service provider used for delivery",
    )
    priority: str = Field(
        default="normal", description="Email priority level (low, normal, high)"
    )

    # Tracking and analytics
    email_opened: bool = Field(
        default=False,
        alias="emailOpened",
        description="Flag indicating if email was opened by recipient",
    )
    open_timestamp: Optional[str] = Field(
        default=None,
        alias="openTimestamp",
        description="Timestamp when email was first opened",
    )
    click_count: int = Field(
        default=0, alias="clickCount", description="Number of link clicks in the email"
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Validate email subject field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email subject must be non-empty")
        if len(v) > 200:
            raise ValueError("Email subject must be at most 200 characters long")
        return v.strip()

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Validate recipient email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Recipient email must be non-empty")
        if "@" not in v:
            raise ValueError("Recipient email must be a valid email address")
        return v.strip().lower()

    @field_validator("email_body")
    @classmethod
    def validate_email_body(cls, v: str) -> str:
        """Validate email body field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email body must be non-empty")
        return v.strip()

    @field_validator("email_format")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format field"""
        allowed_formats = ["html", "text"]
        if v not in allowed_formats:
            raise ValueError(f"Email format must be one of: {allowed_formats}")
        return v

    @field_validator("send_status")
    @classmethod
    def validate_send_status(cls, v: str) -> str:
        """Validate send status field"""
        allowed_statuses = ["pending", "sent", "failed", "bounced", "cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f"Send status must be one of: {allowed_statuses}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority field"""
        allowed_priorities = ["low", "normal", "high"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v

    def schedule_delivery(self, send_time: str) -> None:
        """Schedule the email for delivery at a specific time"""
        self.scheduled_send_time = send_time
        self.send_status = "pending"

    def mark_as_sent(self) -> None:
        """Mark the email as successfully sent"""
        self.send_status = "sent"
        self.actual_send_time = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_as_failed(self, error_message: str) -> None:
        """Mark the email as failed with error message"""
        self.send_status = "failed"
        self.error_message = error_message
        self.retry_count += 1

    def mark_as_delivered(self) -> None:
        """Mark the email as delivered (confirmation received)"""
        self.delivery_confirmation_time = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_as_opened(self) -> None:
        """Mark the email as opened by recipient"""
        if not self.email_opened:
            self.email_opened = True
            self.open_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

    def increment_click_count(self) -> None:
        """Increment the click count for email analytics"""
        self.click_count += 1

    def can_retry(self) -> bool:
        """Check if email delivery can be retried"""
        return self.retry_count < self.max_retries and self.send_status == "failed"

    def attach_report(
        self, report_id: str, file_path: str, file_name: str, file_size: int
    ) -> None:
        """Attach a performance report to the email"""
        self.report_id = report_id
        self.attachment_file_path = file_path
        self.attachment_file_name = file_name
        self.attachment_file_size = file_size

    def generate_weekly_report_email(self, report_summary: str) -> None:
        """Generate standard weekly report email content"""
        self.subject = (
            f"Weekly Product Performance Report - {datetime.now().strftime('%Y-%m-%d')}"
        )
        self.email_body = f"""
        <html>
        <body>
            <h2>Weekly Product Performance Report</h2>
            <p>Dear Sales Team,</p>
            
            <p>Please find attached the weekly product performance analysis report.</p>
            
            <h3>Report Summary:</h3>
            <p>{report_summary}</p>
            
            <p>The detailed report is attached as a PDF file for your review.</p>
            
            <p>Key highlights from this week's analysis are included in the attachment, 
            including sales trends, inventory status, and recommendations for the upcoming week.</p>
            
            <p>Best regards,<br>
            Product Performance Analysis System</p>
        </body>
        </html>
        """
        self.email_format = "html"
        self.recipient_email = "victoria.sagdieva@cyoda.com"

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
