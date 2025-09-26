# entity/report/version_1/report.py

"""
Report Entity for Cyoda Client Application

Represents email reports containing comment analysis summaries.
Manages the generation and delivery of reports as specified in functional requirements.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report entity represents email reports containing comment analysis summaries.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> generating -> ready -> sent/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    title: str = Field(..., description="Report title/subject")
    recipient_email: str = Field(..., description="Email address to send the report to")
    report_period_start: str = Field(
        ..., description="Start date for the reporting period (ISO 8601 format)"
    )
    report_period_end: str = Field(
        ..., description="End date for the reporting period (ISO 8601 format)"
    )

    # Optional fields
    summary_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Aggregated analysis results and metrics"
    )
    generated_at: Optional[str] = Field(
        default=None, description="When the report was generated (ISO 8601 format)"
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        description="When the email was successfully sent (ISO 8601 format)",
    )

    # Processing status fields
    status: Optional[str] = Field(
        default=None, description="Report status (generating, ready, sent, failed)"
    )
    generation_started_at: Optional[str] = Field(
        default=None, description="When report generation started (ISO 8601 format)"
    )
    total_comments: Optional[int] = Field(
        default=None, description="Total number of comments in the report period"
    )
    avg_sentiment: Optional[float] = Field(
        default=None, description="Average sentiment score for the period"
    )
    top_keywords: Optional[list] = Field(
        default=None, description="Top keywords from the analysis period"
    )
    toxicity_summary: Optional[Dict[str, Any]] = Field(
        default=None, description="Summary of toxicity metrics"
    )

    # Email validation regex pattern
    EMAIL_PATTERN: ClassVar[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters long")
        return v.strip()

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Validate recipient_email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Recipient email must be non-empty")

        email = v.strip()
        if not re.match(cls.EMAIL_PATTERN, email):
            raise ValueError("Recipient email must be a valid email address")

        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Recipient email must be at most 254 characters long")

        return email

    @field_validator("report_period_start")
    @classmethod
    def validate_report_period_start(cls, v: str) -> str:
        """Validate report_period_start field (ISO 8601 format)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report period start must be non-empty")
        try:
            # Try to parse the timestamp to validate format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Report period start must be in ISO 8601 format")
        return v.strip()

    @field_validator("report_period_end")
    @classmethod
    def validate_report_period_end(cls, v: str) -> str:
        """Validate report_period_end field (ISO 8601 format)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report period end must be non-empty")
        try:
            # Try to parse the timestamp to validate format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Report period end must be in ISO 8601 format")
        return v.strip()

    @field_validator("total_comments")
    @classmethod
    def validate_total_comments(cls, v: Optional[int]) -> Optional[int]:
        """Validate total_comments field"""
        if v is not None and v < 0:
            raise ValueError("Total comments must be non-negative")
        return v

    @field_validator("avg_sentiment")
    @classmethod
    def validate_avg_sentiment(cls, v: Optional[float]) -> Optional[float]:
        """Validate avg_sentiment field (must be between -1 and 1)"""
        if v is not None:
            if v < -1.0 or v > 1.0:
                raise ValueError("Average sentiment must be between -1 and 1")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Report":
        """Validate business logic rules"""
        # Validate that report period end is after start
        try:
            start_dt = datetime.fromisoformat(
                self.report_period_start.replace("Z", "+00:00")
            )
            end_dt = datetime.fromisoformat(
                self.report_period_end.replace("Z", "+00:00")
            )

            if end_dt <= start_dt:
                raise ValueError("Report period end must be after report period start")
        except ValueError as e:
            if "Report period end must be after" in str(e):
                raise e
            # If it's a parsing error, it was already caught by field validators

        # Ensure summary_data is a dictionary if provided
        if self.summary_data is not None and not isinstance(self.summary_data, dict):
            raise ValueError("Summary data must be a dictionary")

        # Ensure top_keywords is a list if provided
        if self.top_keywords is not None and not isinstance(self.top_keywords, list):
            raise ValueError("Top keywords must be a list")

        return self

    def set_generated_at(self) -> None:
        """Set the generated_at timestamp to current time"""
        self.generated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_email_sent_at(self) -> None:
        """Set the email_sent_at timestamp to current time"""
        self.email_sent_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_generation_started_at(self) -> None:
        """Set the generation_started_at timestamp to current time"""
        self.generation_started_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_report_metrics(
        self,
        total_comments: int,
        avg_sentiment: float,
        top_keywords: list,
        toxicity_summary: Dict[str, Any],
    ) -> None:
        """Set report metrics and update timestamp"""
        self.total_comments = total_comments
        self.avg_sentiment = avg_sentiment
        self.top_keywords = top_keywords
        self.toxicity_summary = toxicity_summary
        self.update_timestamp()

    def compile_final_summary(self) -> Dict[str, Any]:
        """Compile final summary data for the report"""
        summary = {
            "period": {
                "start": self.report_period_start,
                "end": self.report_period_end,
            },
            "metrics": {
                "total_comments": self.total_comments or 0,
                "avg_sentiment": self.avg_sentiment or 0.0,
                "top_keywords": self.top_keywords or [],
                "toxicity_summary": self.toxicity_summary or {},
            },
            "generated_at": self.generated_at,
        }
        self.summary_data = summary
        return summary

    def is_generating(self) -> bool:
        """Check if report is currently being generated"""
        return self.state == "generating"

    def is_ready(self) -> bool:
        """Check if report is ready for sending"""
        return self.state == "ready"

    def is_sent(self) -> bool:
        """Check if report has been sent"""
        return self.state == "sent"

    def is_failed(self) -> bool:
        """Check if report generation or sending failed"""
        return self.state == "failed"

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
