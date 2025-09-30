# entity/report/version_1/report.py

"""
Report Entity for Pet Store Performance Analysis System

Represents weekly performance reports with aggregated data and insights
as specified in the functional requirements for automated reporting.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report represents a weekly performance analysis report for the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> generated -> validated -> emailed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report metadata
    title: str = Field(..., description="Report title")
    report_type: str = Field(
        default="weekly_performance",
        alias="reportType",
        description="Type of report (weekly_performance, monthly_summary, etc.)"
    )
    period_start: str = Field(
        ...,
        alias="periodStart", 
        description="Start date of reporting period (ISO 8601)"
    )
    period_end: str = Field(
        ...,
        alias="periodEnd",
        description="End date of reporting period (ISO 8601)"
    )
    
    # Report content and insights
    executive_summary: Optional[str] = Field(
        default=None,
        alias="executiveSummary",
        description="Brief overview of key findings"
    )
    total_products_analyzed: Optional[int] = Field(
        default=0,
        alias="totalProductsAnalyzed",
        description="Number of products included in analysis"
    )
    
    # Performance metrics
    top_performers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        alias="topPerformers",
        description="List of highest-selling products"
    )
    underperformers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="List of slow-moving products"
    )
    restock_recommendations: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        alias="restockRecommendations",
        description="Products requiring restocking"
    )
    
    # Financial insights
    total_revenue: Optional[float] = Field(
        default=0.0,
        alias="totalRevenue",
        description="Total revenue for the period"
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        alias="revenueGrowth",
        description="Revenue growth percentage vs previous period"
    )
    
    # Email delivery tracking
    email_recipient: str = Field(
        default="victoria.sagdieva@cyoda.com",
        alias="emailRecipient",
        description="Email address for report delivery"
    )
    email_sent: Optional[bool] = Field(
        default=False,
        alias="emailSent",
        description="Flag indicating if email was sent successfully"
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when email was sent"
    )
    
    # Report generation metadata
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated"
    )
    generated_by: str = Field(
        default="ReportGenerationProcessor",
        alias="generatedBy",
        description="System component that generated the report"
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "weekly_performance", "monthly_summary", "quarterly_review"
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

    @field_validator("email_recipient")
    @classmethod
    def validate_email_recipient(cls, v: str) -> str:
        """Validate email recipient"""
        if not v or "@" not in v:
            raise ValueError("Valid email address is required")
        return v.strip().lower()

    @field_validator("total_products_analyzed")
    @classmethod
    def validate_total_products(cls, v: Optional[int]) -> Optional[int]:
        """Validate total products count"""
        if v is not None and v < 0:
            raise ValueError("Total products analyzed cannot be negative")
        return v

    @field_validator("total_revenue")
    @classmethod
    def validate_total_revenue(cls, v: Optional[float]) -> Optional[float]:
        """Validate total revenue"""
        if v is not None and v < 0:
            raise ValueError("Total revenue cannot be negative")
        return v

    def mark_generated(self) -> None:
        """Mark report as generated with timestamp"""
        self.generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_email_sent(self) -> None:
        """Mark email as sent with timestamp"""
        self.email_sent = True
        self.email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

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
            self.generated_at is not None and
            self.executive_summary is not None and
            not self.email_sent
        )

    def get_period_duration_days(self) -> int:
        """Calculate the duration of the reporting period in days"""
        try:
            start = datetime.fromisoformat(self.period_start.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.period_end.replace("Z", "+00:00"))
            return (end - start).days
        except Exception:
            return 7  # Default to weekly

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
