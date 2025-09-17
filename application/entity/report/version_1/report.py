# entity/report/version_1/report.py

"""
Report for Cyoda Client Application

Generates and sends email reports to subscribers based on data analysis results.
Represents report generation and email delivery operations.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report represents a report generation and email delivery operation.

    Manages analysis references, subscriber lists, report content, and delivery status.
    The state field manages workflow states: initial_state -> pending -> generating -> sending -> completed/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    analysis_id: str = Field(
        ..., alias="analysisId", description="Reference to the DataAnalysis entity"
    )
    subscribers: List[str] = Field(
        ..., description="List of email addresses to send report to"
    )

    # Optional fields populated during processing
    report_content: Optional[str] = Field(
        default=None, alias="reportContent", description="Generated report content"
    )
    sent_at: Optional[str] = Field(
        default=None,
        alias="sentAt",
        description="When report was sent (ISO 8601 format)",
    )
    delivery_status: str = Field(
        default="pending",
        alias="deliveryStatus",
        description="Email delivery status (pending, sent, failed)",
    )

    # Validation rules
    ALLOWED_DELIVERY_STATUSES: ClassVar[list[str]] = ["pending", "sent", "failed"]

    @field_validator("analysis_id")
    @classmethod
    def validate_analysis_id(cls, v: str) -> str:
        """Validate analysis_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Analysis ID must be non-empty")
        return v.strip()

    @field_validator("subscribers")
    @classmethod
    def validate_subscribers(cls, v: List[str]) -> List[str]:
        """Validate subscribers field"""
        if not v or len(v) == 0:
            raise ValueError("At least one subscriber email is required")

        # Basic email validation
        for email in v:
            if not email or "@" not in email or "." not in email:
                raise ValueError(f"Invalid email address: {email}")

        return v

    @field_validator("delivery_status")
    @classmethod
    def validate_delivery_status(cls, v: str) -> str:
        """Validate delivery_status field"""
        if v not in cls.ALLOWED_DELIVERY_STATUSES:
            raise ValueError(
                f"Delivery status must be one of: {cls.ALLOWED_DELIVERY_STATUSES}"
            )
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_report_content(self, content: str) -> None:
        """Set generated report content"""
        self.report_content = content
        self.update_timestamp()

    def set_email_sent(self) -> None:
        """Mark email as sent successfully"""
        self.delivery_status = "sent"
        self.sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_email_failed(self) -> None:
        """Mark email sending as failed"""
        self.delivery_status = "failed"
        self.update_timestamp()

    def is_email_sent(self) -> bool:
        """Check if email was sent successfully"""
        return self.delivery_status == "sent"

    def is_email_failed(self) -> bool:
        """Check if email sending failed"""
        return self.delivery_status == "failed"

    def is_ready_for_generation(self) -> bool:
        """Check if entity is ready for report generation (in pending state)"""
        return self.state == "pending"

    def is_generating(self) -> bool:
        """Check if report generation is in progress"""
        return self.state == "generating"

    def is_sending(self) -> bool:
        """Check if email sending is in progress"""
        return self.state == "sending"

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
