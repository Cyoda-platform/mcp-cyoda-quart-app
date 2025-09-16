"""
Inventory Entity for Purrfect Pets API

Represents inventory tracking for pets, including available and reserved quantities.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Inventory(CyodaEntity):
    """
    Inventory entity for tracking pet availability and stock levels.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: InStock -> LowStock -> OutOfStock -> Discontinued
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Inventory"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    pet_id: int = Field(..., description="Foreign key to Pet (unique)")
    quantity: int = Field(..., description="Available quantity", ge=0)
    reserved_quantity: int = Field(
        default=0, description="Reserved for pending orders", ge=0
    )
    reorder_level: int = Field(default=1, description="Minimum stock level", ge=0)
    last_restocked: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Last restock date",
    )

    # Timestamps (inherited from CyodaEntity but override for consistency)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the inventory was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the inventory was last updated (ISO 8601 format)",
    )

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity"""
        if v < 0:
            raise ValueError("Quantity must be non-negative")
        return v

    @field_validator("reserved_quantity")
    @classmethod
    def validate_reserved_quantity(cls, v: int) -> int:
        """Validate reserved quantity"""
        if v < 0:
            raise ValueError("Reserved quantity must be non-negative")
        return v

    @field_validator("reorder_level")
    @classmethod
    def validate_reorder_level(cls, v: int) -> int:
        """Validate reorder level"""
        if v < 0:
            raise ValueError("Reorder level must be non-negative")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_last_restocked(self) -> None:
        """Update the last restocked timestamp to current time"""
        self.last_restocked = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def get_available_quantity(self) -> int:
        """Get available quantity (total - reserved)"""
        return max(0, self.quantity - self.reserved_quantity)

    def reserve_quantity(self, amount: int) -> bool:
        """Reserve a specific quantity if available"""
        if amount <= 0:
            return False

        available = self.get_available_quantity()
        if available >= amount:
            self.reserved_quantity += amount
            self.update_timestamp()
            return True
        return False

    def release_quantity(self, amount: int) -> bool:
        """Release reserved quantity"""
        if amount <= 0:
            return False

        if self.reserved_quantity >= amount:
            self.reserved_quantity -= amount
            self.update_timestamp()
            return True
        return False

    def reduce_quantity(self, amount: int) -> bool:
        """Reduce total quantity (for sales)"""
        if amount <= 0:
            return False

        if self.quantity >= amount:
            self.quantity -= amount
            # Also reduce reserved quantity if necessary
            if self.reserved_quantity > self.quantity:
                self.reserved_quantity = self.quantity
            self.update_timestamp()
            return True
        return False

    def add_quantity(self, amount: int) -> bool:
        """Add quantity (for restocking)"""
        if amount <= 0:
            return False

        self.quantity += amount
        self.update_last_restocked()
        return True

    def is_in_stock(self) -> bool:
        """Check if inventory is in stock"""
        return self.state == "InStock"

    def is_low_stock(self) -> bool:
        """Check if inventory is low stock"""
        return self.state == "LowStock"

    def is_out_of_stock(self) -> bool:
        """Check if inventory is out of stock"""
        return self.state == "OutOfStock"

    def is_discontinued(self) -> bool:
        """Check if inventory is discontinued"""
        return self.state == "Discontinued"

    def should_be_low_stock(self) -> bool:
        """Check if inventory should be in low stock state"""
        available = self.get_available_quantity()
        return 0 < available <= self.reorder_level

    def should_be_out_of_stock(self) -> bool:
        """Check if inventory should be out of stock"""
        return self.get_available_quantity() <= 0

    def to_api_response(self) -> dict:
        """Convert to API response format"""
        data = self.model_dump()
        # Add calculated fields
        data["available_quantity"] = self.get_available_quantity()
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
