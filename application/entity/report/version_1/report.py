"""
Report Entity for Product Performance Analysis and Reporting System

Represents generated performance analysis reports including content,
metadata, email status, and delivery information.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report entity represents generated performance analysis reports.

    Manages report content, metadata, email delivery status, and
    performance insights for the sales team.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core report fields
    title: str = Field(..., description="Report title")
    report_type: str = Field(
        default="weekly_performance",
        alias="reportType",
        description="Type of report (weekly_performance, monthly_summary, etc.)",
    )

    # Report content
    content: Optional[str] = Field(
        default=None, description="Main report content in markdown or HTML format"
    )
    summary: Optional[str] = Field(
        default=None, description="Executive summary of the report"
    )

    # Report metadata
    report_period_start: Optional[str] = Field(
        default=None,
        alias="reportPeriodStart",
        description="Start date of the reporting period",
    )
    report_period_end: Optional[str] = Field(
        default=None,
        alias="reportPeriodEnd",
        description="End date of the reporting period",
    )

    # Performance insights
    insights: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="List of performance insights and recommendations",
    )

    # Key metrics
    total_products_analyzed: Optional[int] = Field(
        default=None,
        alias="totalProductsAnalyzed",
        description="Number of products included in analysis",
    )
    total_revenue: Optional[float] = Field(
        default=None, alias="totalRevenue", description="Total revenue for the period"
    )
    top_performing_products: Optional[List[str]] = Field(
        default_factory=list,
        alias="topPerformingProducts",
        description="List of top performing product IDs",
    )
    underperforming_products: Optional[List[str]] = Field(
        default_factory=list,
        alias="underperformingProducts",
        description="List of underperforming product IDs",
    )
    products_needing_restock: Optional[List[str]] = Field(
        default_factory=list,
        alias="productsNeedingRestock",
        description="List of product IDs that need restocking",
    )

    # Email delivery tracking
    email_recipients: Optional[List[str]] = Field(
        default_factory=lambda: ["victoria.sagdieva@cyoda.com"],
        alias="emailRecipients",
        description="List of email recipients",
    )
    email_sent: Optional[bool] = Field(
        default=False, alias="emailSent", description="Whether email has been sent"
    )
    email_sent_at: Optional[str] = Field(
        default=None, alias="emailSentAt", description="Timestamp when email was sent"
    )
    email_subject: Optional[str] = Field(
        default=None, alias="emailSubject", description="Email subject line"
    )

    # Generation metadata
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated",
    )
    generated_by: Optional[str] = Field(
        default="ReportGenerationProcessor",
        alias="generatedBy",
        description="System component that generated the report",
    )

    # File attachments
    attachment_paths: Optional[List[str]] = Field(
        default_factory=list,
        alias="attachmentPaths",
        description="Paths to report attachments (PDF, etc.)",
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "weekly_performance",
        "monthly_summary",
        "quarterly_review",
        "annual_report",
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate report title"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters")
        return v.strip()

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type"""
        if v not in cls.ALLOWED_REPORT_TYPES:
            raise ValueError(f"Report type must be one of: {cls.ALLOWED_REPORT_TYPES}")
        return v

    @field_validator("email_recipients")
    @classmethod
    def validate_email_recipients(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate email recipients"""
        if v is None:
            return ["victoria.sagdieva@cyoda.com"]

        # Basic email validation
        for email in v:
            if "@" not in email or "." not in email:
                raise ValueError(f"Invalid email address: {email}")

        return v

    def mark_generated(self) -> None:
        """Mark report as generated and update timestamp"""
        self.generated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def mark_email_sent(self) -> None:
        """Mark email as sent and update timestamp"""
        self.email_sent = True
        self.email_sent_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def add_insight(
        self, insight_type: str, description: str, priority: str = "medium"
    ) -> None:
        """Add a performance insight to the report"""
        if self.insights is None:
            self.insights = []

        insight = {
            "type": insight_type,
            "description": description,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        self.insights.append(insight)
        self.update_timestamp()

    def set_report_period(self, start_date: str, end_date: str) -> None:
        """Set the reporting period"""
        self.report_period_start = start_date
        self.report_period_end = end_date
        self.update_timestamp()

    def generate_email_subject(self) -> str:
        """Generate email subject line"""
        if self.report_period_start and self.report_period_end:
            subject = f"Weekly Product Performance Report - {self.report_period_start} to {self.report_period_end}"
        else:
            subject = f"Product Performance Report - {self.title}"

        self.email_subject = subject
        return subject

    def is_ready_for_email(self) -> bool:
        """Check if report is ready to be emailed"""
        return (
            self.content is not None
            and self.summary is not None
            and not self.email_sent
            and self.state == "generated"
        )

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the report"""
        return {
            "total_products": self.total_products_analyzed or 0,
            "total_revenue": self.total_revenue or 0.0,
            "top_performers_count": len(self.top_performing_products or []),
            "underperformers_count": len(self.underperforming_products or []),
            "restock_needed_count": len(self.products_needing_restock or []),
            "insights_count": len(self.insights or []),
        }

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
