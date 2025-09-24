# entity/report/version_1/report.py

"""
Report Entity for Product Performance Analysis and Reporting System

Represents generated performance analysis reports containing insights about product performance,
sales trends, and inventory status for the sales team.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report entity represents generated performance analysis reports.
    
    Contains analysis results, insights, and metadata about the report generation process.
    Reports are generated weekly and emailed to the sales team.
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
        description="Start date of the reporting period (ISO 8601 format)"
    )
    period_end: str = Field(
        ...,
        alias="periodEnd", 
        description="End date of the reporting period (ISO 8601 format)"
    )
    
    # Report content and analysis
    summary: str = Field(..., description="Executive summary of the report")
    total_products_analyzed: int = Field(
        default=0,
        alias="totalProductsAnalyzed",
        description="Number of products included in the analysis"
    )
    
    # Performance insights
    top_performing_products: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="topPerformingProducts",
        description="List of top performing products with metrics"
    )
    underperforming_products: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="underperformingProducts",
        description="List of products that need attention"
    )
    low_stock_products: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="lowStockProducts",
        description="Products requiring restocking"
    )
    
    # Sales and revenue metrics
    total_revenue: Optional[float] = Field(
        default=None,
        alias="totalRevenue",
        description="Total revenue for the reporting period"
    )
    average_performance_score: Optional[float] = Field(
        default=None,
        alias="averagePerformanceScore",
        description="Average performance score across all products"
    )
    revenue_growth_percentage: Optional[float] = Field(
        default=None,
        alias="revenueGrowthPercentage",
        description="Revenue growth compared to previous period"
    )
    
    # Category analysis
    category_performance: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="categoryPerformance",
        description="Performance breakdown by product category"
    )
    
    # Report generation metadata
    generated_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="generatedAt",
        description="Timestamp when the report was generated"
    )
    generated_by: str = Field(
        default="system",
        alias="generatedBy",
        description="System or user that generated the report"
    )
    
    # Email delivery information
    email_recipients: List[str] = Field(
        default_factory=lambda: ["victoria.sagdieva@cyoda.com"],
        alias="emailRecipients",
        description="List of email addresses to receive the report"
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when the report was emailed"
    )
    email_status: str = Field(
        default="pending",
        alias="emailStatus",
        description="Email delivery status (pending, sent, failed)"
    )
    
    # File information
    file_path: Optional[str] = Field(
        default=None,
        alias="filePath",
        description="Path to the generated report file (PDF/HTML)"
    )
    file_size: Optional[int] = Field(
        default=None,
        alias="fileSize",
        description="Size of the report file in bytes"
    )
    
    # Data extraction reference
    data_extraction_id: Optional[str] = Field(
        default=None,
        alias="dataExtractionId",
        description="ID of the data extraction job used for this report"
    )

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the report was created",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the report was last updated",
    )

    # Validation constants
    ALLOWED_REPORT_TYPES: ClassVar[List[str]] = [
        "weekly_performance", "monthly_summary", "quarterly_review", "annual_report"
    ]
    ALLOWED_EMAIL_STATUSES: ClassVar[List[str]] = ["pending", "sent", "failed", "retry"]

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
    def validate_email_status(cls, v: str) -> str:
        """Validate email status"""
        if v not in cls.ALLOWED_EMAIL_STATUSES:
            raise ValueError(f"Email status must be one of: {cls.ALLOWED_EMAIL_STATUSES}")
        return v

    @field_validator("total_products_analyzed")
    @classmethod
    def validate_total_products(cls, v: int) -> int:
        """Validate total products analyzed"""
        if v < 0:
            raise ValueError("Total products analyzed must be non-negative")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_email_sent(self) -> None:
        """Mark the report as successfully emailed"""
        self.email_status = "sent"
        self.email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_email_failed(self) -> None:
        """Mark the report email as failed"""
        self.email_status = "failed"
        self.update_timestamp()

    def set_file_info(self, file_path: str, file_size: int) -> None:
        """Set file information for the generated report"""
        self.file_path = file_path
        self.file_size = file_size
        self.update_timestamp()

    def add_performance_insights(
        self,
        top_products: List[Dict[str, Any]],
        underperforming: List[Dict[str, Any]],
        low_stock: List[Dict[str, Any]]
    ) -> None:
        """Add performance insights to the report"""
        self.top_performing_products = top_products
        self.underperforming_products = underperforming
        self.low_stock_products = low_stock
        self.update_timestamp()

    def calculate_summary_metrics(self) -> None:
        """Calculate and set summary metrics"""
        if self.top_performing_products:
            self.total_products_analyzed = len(self.top_performing_products)
        self.update_timestamp()

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
