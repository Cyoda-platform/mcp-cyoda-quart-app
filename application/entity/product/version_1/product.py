# entity/product/version_1/product.py

"""
Product Entity for Pet Store Performance Analysis System

Represents pet store products with sales data, stock levels, and performance metrics
as specified in functional requirements for automated data extraction and analysis.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Product(CyodaEntity):
    """
    Product represents a pet store product with performance metrics and sales data.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> extracted -> analyzed -> reported
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Product"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core product fields from Pet Store API
    name: str = Field(..., description="Product name from Pet Store API")
    category: str = Field(..., description="Product category (e.g., Dogs, Cats, Birds)")
    status: str = Field(..., description="Product status (available, pending, sold)")
    
    # Performance metrics fields
    sales_volume: Optional[int] = Field(
        default=0,
        alias="salesVolume", 
        description="Total units sold"
    )
    revenue: Optional[float] = Field(
        default=0.0,
        description="Total revenue generated"
    )
    stock_level: Optional[int] = Field(
        default=0,
        alias="stockLevel",
        description="Current inventory stock level"
    )
    
    # Analysis fields (populated during processing)
    performance_score: Optional[float] = Field(
        default=None,
        alias="performanceScore",
        description="Calculated performance score (0-100)"
    )
    inventory_turnover_rate: Optional[float] = Field(
        default=None,
        alias="inventoryTurnoverRate", 
        description="Inventory turnover rate calculation"
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
        description="Timestamp when performance analysis was last run"
    )
    
    # API source tracking
    api_product_id: Optional[str] = Field(
        default=None,
        alias="apiProductId",
        description="Original product ID from Pet Store API"
    )
    api_source: Optional[str] = Field(
        default="petstore",
        alias="apiSource",
        description="Source API identifier"
    )

    # Validation rules
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "Dogs", "Cats", "Birds", "Fish", "Reptiles", "Small Pets"
    ]
    
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "available", "pending", "sold"
    ]

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

    @field_validator("sales_volume")
    @classmethod
    def validate_sales_volume(cls, v: Optional[int]) -> Optional[int]:
        """Validate sales volume is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Sales volume must be non-negative")
        return v

    @field_validator("revenue")
    @classmethod
    def validate_revenue(cls, v: Optional[float]) -> Optional[float]:
        """Validate revenue is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Revenue must be non-negative")
        return v

    @field_validator("stock_level")
    @classmethod
    def validate_stock_level(cls, v: Optional[int]) -> Optional[int]:
        """Validate stock level is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Stock level must be non-negative")
        return v

    def update_extraction_timestamp(self) -> None:
        """Update the last extracted timestamp to current time"""
        self.last_extracted_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_analysis_timestamp(self) -> None:
        """Update the last analyzed timestamp to current time"""
        self.last_analyzed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_performance_metrics(self, performance_score: float, turnover_rate: float) -> None:
        """Set performance metrics and update analysis timestamp"""
        self.performance_score = performance_score
        self.inventory_turnover_rate = turnover_rate
        self.update_analysis_timestamp()

    def is_low_stock(self, threshold: int = 10) -> bool:
        """Check if product has low stock levels"""
        return self.stock_level is not None and self.stock_level <= threshold

    def is_high_performer(self, threshold: float = 70.0) -> bool:
        """Check if product is a high performer based on score"""
        return self.performance_score is not None and self.performance_score >= threshold

    def needs_restocking(self) -> bool:
        """Check if product needs restocking based on turnover and stock"""
        return (
            self.is_low_stock() and 
            self.inventory_turnover_rate is not None and 
            self.inventory_turnover_rate > 2.0
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
