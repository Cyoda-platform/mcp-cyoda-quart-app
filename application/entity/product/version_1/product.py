# entity/product/version_1/product.py

"""
Product Entity for Cyoda OMS Application

Represents a product with comprehensive schema including attributes, localizations,
media, options, variants, bundles, inventory, compliance, relationships, and events
as specified in the functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Product(CyodaEntity):
    """
    Product entity with comprehensive schema for OMS functionality.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    Contains all fields from the attached Product schema for persistence and round-trip.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Product"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required core fields
    sku: str = Field(..., description="Product SKU - unique identifier")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Default/base price (fallback)")
    quantityAvailable: int = Field(
        ...,
        alias="quantityAvailable",
        description="Quick projection field for available quantity",
    )
    category: str = Field(..., description="Product category")

    # Optional core fields
    warehouseId: Optional[str] = Field(
        default=None, alias="warehouseId", description="Optional default primary node"
    )

    # Complex nested structures
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Product attributes including brand, model, dimensions, weight, hazards, custom",
    )

    localizations: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Localization content with default locale and content array",
    )

    media: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Media files including images and documents"
    )

    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Product options with axes and constraints"
    )

    variants: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Product variants with option values and overrides",
    )

    bundles: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Product bundles (kits or virtual bundles)"
    )

    inventory: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Inventory information with nodes, lots, reservations, policies",
    )

    compliance: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Compliance documents and restrictions"
    )

    relationships: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Supplier and related product relationships"
    )

    events: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Product lifecycle events"
    )

    # Timestamps
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the product was created",
    )
    updatedAt: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the product was last updated",
    )

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        """Validate SKU field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("SKU must be non-empty")
        if len(v) > 100:
            raise ValueError("SKU must be at most 100 characters long")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        if len(v) > 200:
            raise ValueError("Name must be at most 200 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price field"""
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("quantityAvailable")
    @classmethod
    def validate_quantity_available(cls, v: int) -> int:
        """Validate quantity available field"""
        if v < 0:
            raise ValueError("Quantity available must be non-negative")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category must be non-empty")
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updatedAt timestamp to current time"""
        self.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def decrement_quantity(self, amount: int) -> None:
        """Decrement available quantity by specified amount"""
        if amount < 0:
            raise ValueError("Decrement amount must be non-negative")
        if self.quantityAvailable < amount:
            raise ValueError(
                f"Insufficient quantity. Available: {self.quantityAvailable}, Requested: {amount}"
            )
        self.quantityAvailable -= amount
        self.update_timestamp()

    def increment_quantity(self, amount: int) -> None:
        """Increment available quantity by specified amount"""
        if amount < 0:
            raise ValueError("Increment amount must be non-negative")
        self.quantityAvailable += amount
        self.update_timestamp()

    def is_available(self, requested_quantity: int = 1) -> bool:
        """Check if requested quantity is available"""
        return self.quantityAvailable >= requested_quantity

    def to_slim_dto(self) -> Dict[str, Any]:
        """Convert to slim DTO for product list endpoints"""
        return {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantityAvailable": self.quantityAvailable,
            "category": self.category,
            "imageUrl": self._get_primary_image_url(),
        }

    def _get_primary_image_url(self) -> Optional[str]:
        """Get primary image URL from media"""
        if not self.media:
            return None
        for media_item in self.media:
            if media_item.get("type") == "image" and "hero" in media_item.get(
                "tags", []
            ):
                return media_item.get("url")
        # Fallback to first image if no hero image
        for media_item in self.media:
            if media_item.get("type") == "image":
                return media_item.get("url")
        return None

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
