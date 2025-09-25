# entity/report/version_1/report.py

"""
Report Entity for Pet Store Performance Analysis System

Represents weekly performance reports with analysis results, insights, and email dispatch status
as specified in functional requirements for automated reporting to victoria.sagdieva@cyoda.com.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report represents a weekly performance analysis report containing insights,
    trends, and inventory status for automated email dispatch to the sales team.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> generated -> validated -> emailed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report identification and metadata
    report_title: str = Field(..., description="Title of the performance report")
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
    report_type: str = Field(
        default="WEEKLY",
        alias="reportType",
        description="Type of report: WEEKLY, MONTHLY, QUARTERLY",
    )

    # Report content and analysis
    executive_summary: Optional[str] = Field(
        default=None,
        alias="executiveSummary",
        description="Brief overview of key findings and insights",
    )
    total_products_analyzed: Optional[int] = Field(
        default=0,
        alias="totalProductsAnalyzed",
        description="Number of products included in the analysis",
    )
    total_revenue: Optional[float] = Field(
        default=0.0,
        alias="totalRevenue",
        description="Total revenue for the reporting period",
    )

    # Performance insights
    top_performing_products: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="topPerformingProducts",
        description="List of highest-selling products with metrics",
    )
    underperforming_products: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="underperformingProducts",
        description="List of slow-moving products requiring attention",
    )
    low_stock_items: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="lowStockItems", description="Products requiring restocking"
    )

    # Trend analysis
    sales_trends: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="salesTrends",
        description="Sales trend analysis by category and time period",
    )
    inventory_insights: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="inventoryInsights",
        description="Inventory turnover and stock level insights",
    )

    # Email dispatch information
    recipient_email: str = Field(
        default="victoria.sagdieva@cyoda.com",
        alias="recipientEmail",
        description="Email address for report delivery",
    )
    email_status: Optional[str] = Field(
        default="PENDING",
        alias="emailStatus",
        description="Email dispatch status: PENDING, SENT, FAILED",
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when email was sent (ISO 8601 format)",
    )
    email_error_message: Optional[str] = Field(
        default=None,
        alias="emailErrorMessage",
        description="Error message if email dispatch failed",
    )

    # Report generation metadata
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated",
    )
    generated_by: Optional[str] = Field(
        default="ProductPerformanceAnalysisSystem",
        alias="generatedBy",
        description="System or user that generated the report",
    )

    # Report data and attachments
    report_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="reportData",
        description="Complete report data and analysis results",
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "WEEKLY",
        "MONTHLY",
        "QUARTERLY",
        "ANNUAL",
    ]
    ALLOWED_EMAIL_STATUSES: ClassVar[List[str]] = ["PENDING", "SENT", "FAILED", "RETRY"]

    @field_validator("report_title")
    @classmethod
    def validate_report_title(cls, v: str) -> str:
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
            raise ValueError(
                f"Email status must be one of: {cls.ALLOWED_EMAIL_STATUSES}"
            )
        return v

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Validate recipient email format"""
        if not v or "@" not in v:
            raise ValueError("Valid email address is required")
        if len(v) > 100:
            raise ValueError("Email address must be at most 100 characters")
        return v.strip().lower()

    def update_generation_timestamp(self) -> None:
        """Update the generated timestamp to current time"""
        self.generated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_email_sent(self) -> None:
        """Mark email as successfully sent"""
        self.email_status = "SENT"
        self.email_sent_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.email_error_message = None

    def mark_email_failed(self, error_message: str) -> None:
        """Mark email as failed with error message"""
        self.email_status = "FAILED"
        self.email_error_message = error_message
        self.email_sent_at = None

    def set_report_data(self, report_data: Dict[str, Any]) -> None:
        """Set report data and update generation timestamp"""
        self.report_data = report_data
        self.update_generation_timestamp()

    def add_top_performing_product(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the top performing products list"""
        if self.top_performing_products is None:
            self.top_performing_products = []
        self.top_performing_products.append(product_data)

    def add_underperforming_product(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the underperforming products list"""
        if self.underperforming_products is None:
            self.underperforming_products = []
        self.underperforming_products.append(product_data)

    def add_low_stock_item(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the low stock items list"""
        if self.low_stock_items is None:
            self.low_stock_items = []
        self.low_stock_items.append(product_data)

    def is_ready_for_email(self) -> bool:
        """Check if report is ready for email dispatch"""
        return (
            self.report_data is not None
            and self.executive_summary is not None
            and self.email_status == "PENDING"
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
