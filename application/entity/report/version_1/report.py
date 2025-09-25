# entity/report/version_1/report.py

"""
Report Entity for Pet Store Performance Analysis System

Represents a generated performance analysis report containing insights
and summary data for the sales team as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report represents a generated performance analysis report containing
    insights, trends, and summary data for the sales team.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> generated -> emailed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core report fields
    title: str = Field(..., description="Report title")
    report_type: str = Field(
        ...,
        alias="reportType",
        description="Type of report: WEEKLY_SUMMARY, MONTHLY_ANALYSIS, CUSTOM",
    )
    content: Optional[str] = Field(
        default=None, description="Generated report content in markdown or HTML format"
    )

    # Report metadata
    data_period_start: Optional[str] = Field(
        default=None,
        alias="dataPeriodStart",
        description="Start date of the data period covered by this report",
    )
    data_period_end: Optional[str] = Field(
        default=None,
        alias="dataPeriodEnd",
        description="End date of the data period covered by this report",
    )
    generated_by: Optional[str] = Field(
        default="System",
        alias="generatedBy",
        description="Who or what generated this report",
    )

    # Report insights and summary data
    insights: Optional[Dict[str, Any]] = Field(
        default=None, description="Key insights and findings from the analysis"
    )
    summary_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="summaryMetrics",
        description="Summary performance metrics and KPIs",
    )
    product_highlights: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="productHighlights",
        description="Highlighted products (top performers, underperformers, etc.)",
    )

    # Email tracking
    email_recipients: Optional[List[str]] = Field(
        default=None,
        alias="emailRecipients",
        description="List of email addresses to send this report to",
    )
    email_sent: Optional[bool] = Field(
        default=False,
        alias="emailSent",
        description="Whether the report has been emailed",
    )

    # Timestamps
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated",
    )
    emailed_at: Optional[str] = Field(
        default=None, alias="emailedAt", description="Timestamp when report was emailed"
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "WEEKLY_SUMMARY",
        "MONTHLY_ANALYSIS",
        "CUSTOM",
        "PERFORMANCE_ANALYSIS",
        "INVENTORY_REPORT",
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate report title field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) < 5:
            raise ValueError("Report title must be at least 5 characters long")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters long")
        return v.strip()

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type field"""
        if v not in cls.ALLOWED_REPORT_TYPES:
            raise ValueError(f"Report type must be one of: {cls.ALLOWED_REPORT_TYPES}")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate report content field"""
        if v is not None and len(v) > 50000:  # 50KB limit
            raise ValueError("Report content must be at most 50,000 characters long")
        return v

    @field_validator("email_recipients")
    @classmethod
    def validate_email_recipients(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate email recipients list"""
        if v is not None:
            for email in v:
                if not email or "@" not in email:
                    raise ValueError(f"Invalid email address: {email}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Report":
        """Validate business logic rules"""
        # Validate data period consistency
        if self.data_period_start and self.data_period_end:
            try:
                start_date = datetime.fromisoformat(
                    self.data_period_start.replace("Z", "+00:00")
                )
                end_date = datetime.fromisoformat(
                    self.data_period_end.replace("Z", "+00:00")
                )
                if start_date >= end_date:
                    raise ValueError("Data period start must be before end date")
            except ValueError as e:
                if "Data period start must be before end date" in str(e):
                    raise
                raise ValueError("Invalid date format in data period")

        # Validate email sent consistency
        if self.email_sent and not self.emailed_at:
            raise ValueError("If email_sent is True, emailed_at timestamp must be set")

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_generated(
        self, content: str, insights: Dict[str, Any], summary_metrics: Dict[str, Any]
    ) -> None:
        """Mark report as generated with content and insights"""
        self.content = content
        self.insights = insights
        self.summary_metrics = summary_metrics
        self.generated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_emailed(self, recipients: List[str]) -> None:
        """Mark report as emailed to recipients"""
        self.email_recipients = recipients
        self.email_sent = True
        self.emailed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def add_product_highlight(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the highlights list"""
        if self.product_highlights is None:
            self.product_highlights = []
        self.product_highlights.append(product_data)
        self.update_timestamp()

    def set_data_period(self, start_date: str, end_date: str) -> None:
        """Set the data period for this report"""
        self.data_period_start = start_date
        self.data_period_end = end_date
        self.update_timestamp()

    def is_ready_for_email(self) -> bool:
        """Check if report is ready to be emailed"""
        return (
            self.content is not None
            and len(self.content.strip()) > 0
            and self.generated_at is not None
            and not self.email_sent
        )

    def get_report_summary(self) -> Dict[str, Any]:
        """Get a summary of the report for API responses"""
        return {
            "title": self.title,
            "report_type": self.report_type,
            "data_period": {
                "start": self.data_period_start,
                "end": self.data_period_end,
            },
            "generated_at": self.generated_at,
            "email_sent": self.email_sent,
            "content_length": len(self.content) if self.content else 0,
            "insights_count": len(self.insights) if self.insights else 0,
            "highlights_count": (
                len(self.product_highlights) if self.product_highlights else 0
            ),
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
