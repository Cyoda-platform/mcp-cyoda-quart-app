# entity/report/version_1/report.py

"""
Report Entity for Pet Store Performance Analysis System

Represents weekly performance analysis reports with insights and email dispatch status
as specified in functional requirements for automated reporting to sales team.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report represents a weekly performance analysis report for pet store products.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> generated -> validated -> emailed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core report fields
    title: str = Field(..., description="Report title")
    report_type: str = Field(
        default="weekly_performance",
        alias="reportType",
        description="Type of report (weekly_performance, monthly_summary, etc.)"
    )
    report_period_start: str = Field(
        ...,
        alias="reportPeriodStart",
        description="Start date of reporting period (ISO 8601 format)"
    )
    report_period_end: str = Field(
        ...,
        alias="reportPeriodEnd", 
        description="End date of reporting period (ISO 8601 format)"
    )
    
    # Report content and insights
    executive_summary: Optional[str] = Field(
        default=None,
        alias="executiveSummary",
        description="Executive summary of key findings"
    )
    top_performers: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="topPerformers",
        description="List of top performing products"
    )
    underperformers: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of underperforming products"
    )
    restock_recommendations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="restockRecommendations",
        description="Products that need restocking"
    )
    
    # Analytics data
    total_revenue: Optional[float] = Field(
        default=None,
        alias="totalRevenue",
        description="Total revenue for the period"
    )
    total_sales_volume: Optional[int] = Field(
        default=None,
        alias="totalSalesVolume",
        description="Total units sold for the period"
    )
    average_performance_score: Optional[float] = Field(
        default=None,
        alias="averagePerformanceScore",
        description="Average performance score across all products"
    )
    
    # Email dispatch tracking
    email_recipients: List[str] = Field(
        default_factory=lambda: ["victoria.sagdieva@cyoda.com"],
        alias="emailRecipients",
        description="List of email recipients"
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when email was sent (ISO 8601 format)"
    )
    email_status: Optional[str] = Field(
        default="pending",
        alias="emailStatus",
        description="Email dispatch status (pending, sent, failed)"
    )
    email_error: Optional[str] = Field(
        default=None,
        alias="emailError",
        description="Error message if email dispatch failed"
    )
    
    # Report generation metadata
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated"
    )
    generated_by: Optional[str] = Field(
        default="automated_system",
        alias="generatedBy",
        description="System or user that generated the report"
    )
    products_analyzed: Optional[int] = Field(
        default=None,
        alias="productsAnalyzed",
        description="Number of products included in analysis"
    )

    # Validation rules
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "weekly_performance", "monthly_summary", "quarterly_review"
    ]
    
    ALLOWED_EMAIL_STATUSES: ClassVar[List[str]] = [
        "pending", "sent", "failed"
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

    @field_validator("email_status")
    @classmethod
    def validate_email_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate email status"""
        if v is not None and v not in cls.ALLOWED_EMAIL_STATUSES:
            raise ValueError(f"Email status must be one of: {cls.ALLOWED_EMAIL_STATUSES}")
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
                raise ValueError(f"Invalid email format: {email}")
        
        return v

    def update_generation_timestamp(self) -> None:
        """Update the generated timestamp to current time"""
        self.generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_email_sent(self) -> None:
        """Mark email as successfully sent"""
        self.email_status = "sent"
        self.email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.email_error = None

    def mark_email_failed(self, error_message: str) -> None:
        """Mark email as failed with error message"""
        self.email_status = "failed"
        self.email_error = error_message
        self.email_sent_at = None

    def set_analytics_data(self, total_revenue: float, total_volume: int, avg_score: float) -> None:
        """Set analytics data for the report"""
        self.total_revenue = total_revenue
        self.total_sales_volume = total_volume
        self.average_performance_score = avg_score

    def add_top_performer(self, product_data: Dict[str, Any]) -> None:
        """Add a product to top performers list"""
        if self.top_performers is None:
            self.top_performers = []
        self.top_performers.append(product_data)

    def add_underperformer(self, product_data: Dict[str, Any]) -> None:
        """Add a product to underperformers list"""
        if self.underperformers is None:
            self.underperformers = []
        self.underperformers.append(product_data)

    def add_restock_recommendation(self, product_data: Dict[str, Any]) -> None:
        """Add a product to restock recommendations"""
        if self.restock_recommendations is None:
            self.restock_recommendations = []
        self.restock_recommendations.append(product_data)

    def is_ready_for_email(self) -> bool:
        """Check if report is ready to be emailed"""
        return (
            self.executive_summary is not None and
            self.generated_at is not None and
            self.email_status == "pending"
        )

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
