# entity/performance_report/version_1/performance_report.py

"""
PerformanceReport Entity for Product Performance Analysis System

Represents generated analysis reports with summary data, trends, and insights
as specified in functional requirements for weekly reporting.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class PerformanceReport(CyodaEntity):
    """
    PerformanceReport represents generated analysis reports with performance insights.
    
    Stores weekly summary reports including sales trends, inventory status, and
    product performance analysis as specified in functional requirements.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "PerformanceReport"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report metadata
    report_title: str = Field(..., alias="reportTitle", description="Title of the performance report")
    report_period_start: str = Field(
        ..., 
        alias="reportPeriodStart", 
        description="Start date of the reporting period (ISO 8601)"
    )
    report_period_end: str = Field(
        ..., 
        alias="reportPeriodEnd", 
        description="End date of the reporting period (ISO 8601)"
    )
    generation_timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="generationTimestamp",
        description="Timestamp when report was generated"
    )
    
    # Report content and insights
    executive_summary: str = Field(
        ..., 
        alias="executiveSummary", 
        description="Brief overview of key findings and insights"
    )
    
    # Sales trends analysis
    highest_selling_products: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="highestSellingProducts",
        description="List of top performing products with sales data"
    )
    slow_moving_inventory: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="slowMovingInventory", 
        description="List of products with low sales velocity"
    )
    
    # Inventory status
    items_requiring_restock: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="itemsRequiringRestock",
        description="List of products that need restocking"
    )
    total_products_analyzed: int = Field(
        default=0,
        alias="totalProductsAnalyzed",
        description="Total number of products included in analysis"
    )
    
    # Performance metrics summary
    total_revenue: float = Field(
        default=0.0,
        alias="totalRevenue",
        description="Total revenue for the reporting period"
    )
    total_sales_volume: int = Field(
        default=0,
        alias="totalSalesVolume", 
        description="Total sales volume for the reporting period"
    )
    average_inventory_turnover: float = Field(
        default=0.0,
        alias="averageInventoryTurnover",
        description="Average inventory turnover rate across all products"
    )
    
    # Category performance breakdown
    category_performance: Dict[str, Any] = Field(
        default_factory=dict,
        alias="categoryPerformance",
        description="Performance metrics broken down by product category"
    )
    
    # Trends and insights
    performance_trends: List[str] = Field(
        default_factory=list,
        alias="performanceTrends",
        description="List of identified performance trends"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Business recommendations based on analysis"
    )
    
    # Report generation metadata
    data_sources: List[str] = Field(
        default_factory=lambda: ["petstore_api"],
        alias="dataSources",
        description="List of data sources used for the report"
    )
    report_format: str = Field(
        default="pdf",
        alias="reportFormat",
        description="Format of the generated report (pdf, html, json)"
    )
    report_status: str = Field(
        default="draft",
        alias="reportStatus",
        description="Status of the report (draft, finalized, sent)"
    )
    
    # File and email tracking
    report_file_path: Optional[str] = Field(
        default=None,
        alias="reportFilePath",
        description="Path to the generated report file"
    )
    email_sent: bool = Field(
        default=False,
        alias="emailSent",
        description="Flag indicating if report has been emailed"
    )
    email_recipients: List[str] = Field(
        default_factory=lambda: ["victoria.sagdieva@cyoda.com"],
        alias="emailRecipients",
        description="List of email recipients for the report"
    )

    @field_validator("report_title")
    @classmethod
    def validate_report_title(cls, v: str) -> str:
        """Validate report title field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters long")
        return v.strip()

    @field_validator("executive_summary")
    @classmethod
    def validate_executive_summary(cls, v: str) -> str:
        """Validate executive summary field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Executive summary must be non-empty")
        if len(v) > 2000:
            raise ValueError("Executive summary must be at most 2000 characters long")
        return v.strip()

    @field_validator("report_format")
    @classmethod
    def validate_report_format(cls, v: str) -> str:
        """Validate report format field"""
        allowed_formats = ["pdf", "html", "json"]
        if v not in allowed_formats:
            raise ValueError(f"Report format must be one of: {allowed_formats}")
        return v

    @field_validator("report_status")
    @classmethod
    def validate_report_status(cls, v: str) -> str:
        """Validate report status field"""
        allowed_statuses = ["draft", "finalized", "sent", "failed"]
        if v not in allowed_statuses:
            raise ValueError(f"Report status must be one of: {allowed_statuses}")
        return v

    def add_high_performing_product(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the highest selling products list"""
        if product_data not in self.highest_selling_products:
            self.highest_selling_products.append(product_data)

    def add_slow_moving_product(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the slow moving inventory list"""
        if product_data not in self.slow_moving_inventory:
            self.slow_moving_inventory.append(product_data)

    def add_restock_item(self, product_data: Dict[str, Any]) -> None:
        """Add a product to the items requiring restock list"""
        if product_data not in self.items_requiring_restock:
            self.items_requiring_restock.append(product_data)

    def add_performance_trend(self, trend: str) -> None:
        """Add a performance trend to the trends list"""
        if trend not in self.performance_trends:
            self.performance_trends.append(trend)

    def add_recommendation(self, recommendation: str) -> None:
        """Add a business recommendation to the recommendations list"""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def finalize_report(self) -> None:
        """Mark the report as finalized and update timestamp"""
        self.report_status = "finalized"
        self.generation_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_as_sent(self) -> None:
        """Mark the report as sent via email"""
        self.email_sent = True
        self.report_status = "sent"

    def calculate_summary_metrics(self, product_data_list: List[Dict[str, Any]]) -> None:
        """Calculate summary metrics from product data"""
        self.total_products_analyzed = len(product_data_list)
        
        total_revenue = 0.0
        total_sales = 0
        total_turnover = 0.0
        category_stats: Dict[str, Dict[str, Any]] = {}
        
        for product in product_data_list:
            # Aggregate totals
            total_revenue += product.get("revenue", 0.0)
            total_sales += product.get("salesVolume", 0)
            total_turnover += product.get("inventoryTurnoverRate", 0.0)
            
            # Category breakdown
            category = product.get("category", "Unknown")
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "revenue": 0.0,
                    "sales": 0,
                    "turnover": 0.0
                }
            
            category_stats[category]["count"] += 1
            category_stats[category]["revenue"] += product.get("revenue", 0.0)
            category_stats[category]["sales"] += product.get("salesVolume", 0)
            category_stats[category]["turnover"] += product.get("inventoryTurnoverRate", 0.0)
        
        # Set calculated values
        self.total_revenue = total_revenue
        self.total_sales_volume = total_sales
        self.average_inventory_turnover = total_turnover / max(self.total_products_analyzed, 1)
        
        # Calculate category averages
        for category, stats in category_stats.items():
            count = stats["count"]
            category_stats[category]["avg_turnover"] = stats["turnover"] / count
            category_stats[category]["avg_revenue_per_product"] = stats["revenue"] / count
        
        self.category_performance = category_stats

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
