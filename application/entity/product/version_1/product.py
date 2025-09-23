"""
Product Entity for Product Performance Analysis and Reporting System

Represents product data retrieved from the Pet Store API including
product details, pricing, inventory levels, and performance metrics.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Product(CyodaEntity):
    """
    Product entity represents product data from Pet Store API.

    Manages product information including name, category, status, pricing,
    inventory levels, and performance metrics for analysis and reporting.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Product"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core product fields from Pet Store API
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    status: str = Field(..., description="Product status (available, pending, sold)")

    # Pricing information
    price: Optional[float] = Field(default=None, description="Product price")

    # Inventory tracking
    inventory_level: Optional[int] = Field(
        default=None, alias="inventoryLevel", description="Current inventory level"
    )

    # Pet Store API specific fields
    pet_store_id: Optional[str] = Field(
        default=None, alias="petStoreId", description="ID from Pet Store API"
    )

    # Performance metrics (populated during analysis)
    sales_volume: Optional[int] = Field(
        default=None, alias="salesVolume", description="Total sales volume"
    )
    revenue: Optional[float] = Field(
        default=None, description="Total revenue generated"
    )
    inventory_turnover_rate: Optional[float] = Field(
        default=None,
        alias="inventoryTurnoverRate",
        description="Inventory turnover rate",
    )

    # Analysis metadata
    last_analyzed_at: Optional[str] = Field(
        default=None,
        alias="lastAnalyzedAt",
        description="Timestamp when product was last analyzed",
    )
    performance_score: Optional[float] = Field(
        default=None,
        alias="performanceScore",
        description="Calculated performance score (0-100)",
    )

    # Data extraction metadata
    extracted_at: Optional[str] = Field(
        default=None,
        alias="extractedAt",
        description="Timestamp when data was extracted from API",
    )
    extraction_source: Optional[str] = Field(
        default="pet_store_api",
        alias="extractionSource",
        description="Source of the data extraction",
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[list[str]] = ["available", "pending", "sold"]
    ALLOWED_CATEGORIES: ClassVar[list[str]] = [
        "Dogs",
        "Cats",
        "Birds",
        "Fish",
        "Reptiles",
        "Small Pets",
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

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate product status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate product price"""
        if v is not None and v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("inventory_level")
    @classmethod
    def validate_inventory_level(cls, v: Optional[int]) -> Optional[int]:
        """Validate inventory level"""
        if v is not None and v < 0:
            raise ValueError("Inventory level must be non-negative")
        return v

    def update_analysis_timestamp(self) -> None:
        """Update the last analyzed timestamp"""
        self.last_analyzed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def update_extraction_timestamp(self) -> None:
        """Update the extraction timestamp"""
        self.extracted_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def calculate_performance_score(self) -> float:
        """Calculate performance score based on available metrics"""
        if not self.sales_volume and not self.revenue:
            return 0.0

        # Simple scoring algorithm
        score = 0.0

        # Sales volume component (0-40 points)
        if self.sales_volume:
            score += min(40, self.sales_volume * 2)

        # Revenue component (0-40 points)
        if self.revenue:
            score += min(40, self.revenue / 10)

        # Inventory turnover component (0-20 points)
        if self.inventory_turnover_rate:
            score += min(20, self.inventory_turnover_rate * 10)

        self.performance_score = min(100.0, score)
        return self.performance_score

    def is_low_stock(self, threshold: int = 10) -> bool:
        """Check if product has low stock levels"""
        return self.inventory_level is not None and self.inventory_level <= threshold

    def is_high_performer(self, threshold: float = 70.0) -> bool:
        """Check if product is a high performer"""
        return (
            self.performance_score is not None and self.performance_score >= threshold
        )

    def needs_restocking(self) -> bool:
        """Check if product needs restocking based on status and inventory"""
        return (
            self.status == "available"
            and self.inventory_level is not None
            and self.inventory_level <= 5
        )

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
