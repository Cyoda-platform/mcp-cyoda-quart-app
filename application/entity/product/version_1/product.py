# entity/product/version_1/product.py

"""
Product Entity for Pet Store Performance Analysis System

Represents pet store products with sales data, inventory levels, and performance metrics
as specified in the functional requirements for automated data extraction and analysis.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Product(CyodaEntity):
    """
    Product represents a pet store product with performance metrics and sales data.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> extracted -> analyzed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Product"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core product information from Pet Store API
    name: str = Field(..., description="Product name from Pet Store API")
    category: str = Field(..., description="Product category (e.g., dog, cat, bird)")
    status: str = Field(..., description="Product status (available, pending, sold)")
    
    # Performance metrics for analysis
    sales_volume: Optional[int] = Field(
        default=0,
        alias="salesVolume", 
        description="Total units sold"
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
    
    # Analysis results (populated by processors)
    performance_score: Optional[float] = Field(
        default=None,
        alias="performanceScore",
        description="Calculated performance score (0-100)"
    )
    trend_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="trendAnalysis",
        description="Trend analysis data"
    )
    requires_restocking: Optional[bool] = Field(
        default=None,
        alias="requiresRestocking",
        description="Flag indicating if product needs restocking"
    )
    
    # Timestamps
    last_analyzed: Optional[str] = Field(
        default=None,
        alias="lastAnalyzed",
        description="Timestamp when product was last analyzed"
    )
    
    # Pet Store API specific fields
    pet_store_id: Optional[int] = Field(
        default=None,
        alias="petStoreId",
        description="Original ID from Pet Store API"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Product tags from Pet Store API"
    )

    # Validation constants
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "dog", "cat", "bird", "fish", "reptile", "small-pet"
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
        """Validate sales volume"""
        if v is not None and v < 0:
            raise ValueError("Sales volume cannot be negative")
        return v

    @field_validator("revenue")
    @classmethod
    def validate_revenue(cls, v: Optional[float]) -> Optional[float]:
        """Validate revenue"""
        if v is not None and v < 0:
            raise ValueError("Revenue cannot be negative")
        return v

    @field_validator("inventory_level")
    @classmethod
    def validate_inventory_level(cls, v: Optional[int]) -> Optional[int]:
        """Validate inventory level"""
        if v is not None and v < 0:
            raise ValueError("Inventory level cannot be negative")
        return v

    def update_analysis_timestamp(self) -> None:
        """Update the last analyzed timestamp"""
        self.last_analyzed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_performance_data(self, score: float, trend_data: Dict[str, Any], needs_restock: bool) -> None:
        """Set performance analysis results"""
        self.performance_score = score
        self.trend_analysis = trend_data
        self.requires_restocking = needs_restock
        self.update_analysis_timestamp()

    def is_high_performer(self) -> bool:
        """Check if product is a high performer"""
        return self.performance_score is not None and self.performance_score >= 80

    def is_underperforming(self) -> bool:
        """Check if product is underperforming"""
        return self.performance_score is not None and self.performance_score < 40

    def needs_attention(self) -> bool:
        """Check if product needs attention (low stock or underperforming)"""
        return (
            self.requires_restocking is True or 
            self.is_underperforming() or
            (self.inventory_level is not None and self.inventory_level < 10)
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
