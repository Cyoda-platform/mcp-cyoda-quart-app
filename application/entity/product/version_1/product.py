# entity/product/version_1/product.py

"""
Product Entity for Pet Store Performance Analysis System

Represents pet store products with sales data, inventory levels, and performance metrics
as specified in functional requirements for automated data extraction and analysis.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Product(CyodaEntity):
    """
    Product represents a pet store product with sales data, inventory levels,
    and performance metrics for automated analysis and reporting.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> extracted -> analyzed -> reported
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Product"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core product information from Pet Store API
    product_id: str = Field(..., description="Unique product ID from Pet Store API")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category (e.g., dog, cat, bird)")
    status: str = Field(..., description="Product status (available, pending, sold)")
    
    # Sales and inventory data
    price: Optional[float] = Field(default=None, description="Product price")
    sales_volume: Optional[int] = Field(
        default=0, 
        alias="salesVolume",
        description="Number of units sold"
    )
    revenue: Optional[float] = Field(
        default=0.0,
        description="Total revenue generated"
    )
    inventory_level: Optional[int] = Field(
        default=0,
        alias="inventoryLevel", 
        description="Current stock level"
    )
    
    # Performance metrics (calculated during analysis)
    inventory_turnover_rate: Optional[float] = Field(
        default=None,
        alias="inventoryTurnoverRate",
        description="Inventory turnover rate calculated during analysis"
    )
    performance_score: Optional[float] = Field(
        default=None,
        alias="performanceScore",
        description="Overall performance score (0-100)"
    )
    trend_indicator: Optional[str] = Field(
        default=None,
        alias="trendIndicator",
        description="Trend indicator: RISING, FALLING, STABLE"
    )
    
    # Timestamps
    last_extracted_at: Optional[str] = Field(
        default=None,
        alias="lastExtractedAt",
        description="Timestamp when data was last extracted from API"
    )
    last_analyzed_at: Optional[str] = Field(
        default=None,
        alias="lastAnalyzedAt", 
        description="Timestamp when performance analysis was last performed"
    )
    
    # Analysis results
    analysis_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="analysisData",
        description="Detailed analysis results and metrics"
    )
    
    # Validation constants
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "dog", "cat", "bird", "fish", "reptile", "small-pet"
    ]
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "available", "pending", "sold"
    ]
    ALLOWED_TRENDS: ClassVar[List[str]] = [
        "RISING", "FALLING", "STABLE"
    ]

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        """Validate product ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Product ID must be non-empty")
        if len(v) > 50:
            raise ValueError("Product ID must be at most 50 characters")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate product name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Product name must be non-empty")
        if len(v) > 200:
            raise ValueError("Product name must be at most 200 characters")
        return v.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate product category"""
        if v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate product status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("trend_indicator")
    @classmethod
    def validate_trend_indicator(cls, v: Optional[str]) -> Optional[str]:
        """Validate trend indicator"""
        if v is not None and v not in cls.ALLOWED_TRENDS:
            raise ValueError(f"Trend indicator must be one of: {cls.ALLOWED_TRENDS}")
        return v

    def update_extraction_timestamp(self) -> None:
        """Update the last extracted timestamp to current time"""
        self.last_extracted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_analysis_timestamp(self) -> None:
        """Update the last analyzed timestamp to current time"""
        self.last_analyzed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_analysis_data(self, analysis_data: Dict[str, Any]) -> None:
        """Set analysis data and update timestamp"""
        self.analysis_data = analysis_data
        self.update_analysis_timestamp()

    def calculate_revenue(self) -> float:
        """Calculate total revenue from sales volume and price"""
        if self.sales_volume and self.price:
            self.revenue = self.sales_volume * self.price
            return self.revenue
        return 0.0

    def is_low_stock(self, threshold: int = 10) -> bool:
        """Check if product is low on stock"""
        return (self.inventory_level or 0) <= threshold

    def is_high_performer(self, threshold: float = 70.0) -> bool:
        """Check if product is a high performer based on performance score"""
        return (self.performance_score or 0.0) >= threshold

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
