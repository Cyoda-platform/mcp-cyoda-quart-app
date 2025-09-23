# entity/report/version_1/report.py

"""
Report Entity for Pet Store Performance Analysis System

Represents a weekly performance analysis report that contains insights,
trends, and recommendations for the sales team as specified in
functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report entity represents a weekly performance analysis report containing
    product insights, sales trends, and inventory recommendations.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> generated -> reviewed -> sent
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report identification and metadata
    report_title: str = Field(
        ..., alias="reportTitle", description="Title of the performance report"
    )
    report_type: str = Field(
        default="WEEKLY_PERFORMANCE",
        alias="reportType",
        description="Type of report (WEEKLY_PERFORMANCE, MONTHLY_SUMMARY, etc.)",
    )
    report_period_start: str = Field(
        ...,
        alias="reportPeriodStart",
        description="Start date of the reporting period (ISO 8601 format)",
    )
    report_period_end: str = Field(
        ...,
        alias="reportPeriodEnd",
        description="End date of the reporting period (ISO 8601 format)",
    )

    # Report content and analysis
    total_products_analyzed: int = Field(
        default=0,
        alias="totalProductsAnalyzed",
        description="Total number of products included in the analysis",
    )
    high_performers: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="highPerformers",
        description="List of high-performing products with metrics",
    )
    underperformers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of underperforming products needing attention",
    )
    restock_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="restockRecommendations",
        description="List of products requiring restocking",
    )

    # Summary metrics
    total_revenue: Optional[float] = Field(
        default=0.0,
        alias="totalRevenue",
        description="Total revenue for the reporting period",
    )
    total_sales_volume: Optional[int] = Field(
        default=0,
        alias="totalSalesVolume",
        description="Total units sold during the reporting period",
    )
    average_performance_score: Optional[float] = Field(
        default=0.0,
        alias="averagePerformanceScore",
        description="Average performance score across all products",
    )

    # Trend analysis
    trending_categories: List[str] = Field(
        default_factory=list,
        alias="trendingCategories",
        description="List of trending product categories",
    )
    declining_categories: List[str] = Field(
        default_factory=list,
        alias="decliningCategories",
        description="List of declining product categories",
    )

    # Report generation and delivery
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when the report was generated",
    )
    generated_by: str = Field(
        default="ProductAnalysisSystem",
        alias="generatedBy",
        description="System or user that generated the report",
    )
    email_recipients: List[str] = Field(
        default_factory=lambda: ["victoria.sagdieva@cyoda.com"],
        alias="emailRecipients",
        description="List of email addresses to receive the report",
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when the report was emailed",
    )
    email_status: str = Field(
        default="PENDING",
        alias="emailStatus",
        description="Status of email delivery (PENDING, SENT, FAILED)",
    )

    # Report format and content
    report_format: str = Field(
        default="PDF",
        alias="reportFormat",
        description="Format of the report (PDF, HTML, JSON)",
    )
    report_content: Optional[str] = Field(
        default=None,
        alias="reportContent",
        description="Generated report content (HTML, JSON, etc.)",
    )
    executive_summary: Optional[str] = Field(
        default=None,
        alias="executiveSummary",
        description="Executive summary of key findings",
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "WEEKLY_PERFORMANCE",
        "MONTHLY_SUMMARY",
        "QUARTERLY_REVIEW",
        "ANNUAL_REPORT",
    ]
    ALLOWED_EMAIL_STATUSES: ClassVar[List[str]] = ["PENDING", "SENT", "FAILED", "RETRY"]
    ALLOWED_FORMATS: ClassVar[List[str]] = ["PDF", "HTML", "JSON", "CSV"]

    @field_validator("report_title")
    @classmethod
    def validate_report_title(cls, v: str) -> str:
        """Validate report title"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters long")
        return v.strip()

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type"""
        if v not in cls.ALLOWED_REPORT_TYPES:
            raise ValueError(f"Report type must be one of: {cls.ALLOWED_REPORT_TYPES}")
        return v

    @field_validator("email_status")
    @classmethod
    def validate_email_status(cls, v: str) -> str:
        """Validate email status"""
        if v not in cls.ALLOWED_EMAIL_STATUSES:
            raise ValueError(
                f"Email status must be one of: {cls.ALLOWED_EMAIL_STATUSES}"
            )
        return v

    @field_validator("report_format")
    @classmethod
    def validate_report_format(cls, v: str) -> str:
        """Validate report format"""
        if v not in cls.ALLOWED_FORMATS:
            raise ValueError(f"Report format must be one of: {cls.ALLOWED_FORMATS}")
        return v

    @field_validator("email_recipients")
    @classmethod
    def validate_email_recipients(cls, v: List[str]) -> List[str]:
        """Validate email recipients list"""
        if not v or len(v) == 0:
            raise ValueError("At least one email recipient is required")

        # Basic email validation
        for email in v:
            if "@" not in email or "." not in email:
                raise ValueError(f"Invalid email address: {email}")

        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Report":
        """Validate business logic rules"""
        # Report period end should be after start
        try:
            start_date = datetime.fromisoformat(
                self.report_period_start.replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(
                self.report_period_end.replace("Z", "+00:00")
            )

            if end_date <= start_date:
                raise ValueError("Report period end must be after start date")
        except ValueError as e:
            if "Report period end must be after start date" in str(e):
                raise
            # If date parsing fails, that's a separate validation issue

        # If email was sent, email_sent_at should be set
        if self.email_status == "SENT" and not self.email_sent_at:
            raise ValueError("Email sent timestamp must be set when status is SENT")

        return self

    def update_generation_timestamp(self) -> None:
        """Update the generated_at timestamp to current time"""
        self.generated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_email_sent(self) -> None:
        """Mark the report as successfully emailed"""
        self.email_status = "SENT"
        self.email_sent_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_email_failed(self) -> None:
        """Mark the email delivery as failed"""
        self.email_status = "FAILED"

    def add_high_performer(self, product_data: Dict[str, Any]) -> None:
        """Add a high-performing product to the report"""
        self.high_performers.append(product_data)

    def add_underperformer(self, product_data: Dict[str, Any]) -> None:
        """Add an underperforming product to the report"""
        self.underperformers.append(product_data)

    def add_restock_recommendation(self, product_data: Dict[str, Any]) -> None:
        """Add a restocking recommendation to the report"""
        self.restock_recommendations.append(product_data)

    def calculate_summary_metrics(self) -> None:
        """Calculate summary metrics from product data"""
        # This would typically be called by a processor
        total_products = len(self.high_performers) + len(self.underperformers)
        self.total_products_analyzed = total_products

    def generate_executive_summary(self) -> str:
        """Generate an executive summary of the report"""
        summary_parts = []

        summary_parts.append(
            f"Performance Analysis Report for {self.report_period_start} to {self.report_period_end}"
        )
        summary_parts.append(f"Total Products Analyzed: {self.total_products_analyzed}")

        if self.total_revenue:
            summary_parts.append(f"Total Revenue: ${self.total_revenue:,.2f}")

        if self.total_sales_volume:
            summary_parts.append(f"Total Units Sold: {self.total_sales_volume:,}")

        if self.high_performers:
            summary_parts.append(
                f"High Performers: {len(self.high_performers)} products"
            )

        if self.underperformers:
            summary_parts.append(
                f"Underperformers: {len(self.underperformers)} products"
            )

        if self.restock_recommendations:
            summary_parts.append(
                f"Restock Needed: {len(self.restock_recommendations)} products"
            )

        self.executive_summary = "\n".join(summary_parts)
        return self.executive_summary

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
