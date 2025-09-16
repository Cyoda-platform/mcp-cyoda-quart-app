"""
OrderItem Entity for Purrfect Pets API

Represents an individual item within an order, linking pets to orders with quantity and pricing.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class OrderItem(CyodaEntity):
    """
    OrderItem entity representing individual items within an order.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: Added -> Confirmed -> Cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "OrderItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    order_id: int = Field(..., description="Foreign key to Order")
    pet_id: int = Field(..., description="Foreign key to Pet")
    quantity: int = Field(..., description="Quantity of pets", ge=1)
    unit_price: float = Field(..., description="Price per unit", ge=0)
    total_price: float = Field(..., description="Total price (quantity * unit_price)", ge=0)

    # Timestamps (inherited from CyodaEntity but override for consistency)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="Timestamp when the order item was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the order item was last updated (ISO 8601 format)",
    )

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity"""
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: float) -> float:
        """Validate unit price"""
        if v < 0:
            raise ValueError("Unit price must be non-negative")
        return v

    @field_validator("total_price")
    @classmethod
    def validate_total_price(cls, v: float) -> float:
        """Validate total price"""
        if v < 0:
            raise ValueError("Total price must be non-negative")
        return v

    @model_validator(mode="after")
    def validate_total_price_calculation(self) -> "OrderItem":
        """Validate that total_price equals quantity * unit_price"""
        expected_total = self.quantity * self.unit_price
        if abs(self.total_price - expected_total) > 0.01:  # Allow for small floating point differences
            raise ValueError(f"Total price ({self.total_price}) must equal quantity ({self.quantity}) * unit_price ({self.unit_price}) = {expected_total}")
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def calculate_total_price(self) -> None:
        """Calculate and set total price based on quantity and unit price"""
        self.total_price = self.quantity * self.unit_price
        self.update_timestamp()

    def is_added(self) -> bool:
        """Check if order item is added"""
        return self.state == "Added"

    def is_confirmed(self) -> bool:
        """Check if order item is confirmed"""
        return self.state == "Confirmed"

    def is_cancelled(self) -> bool:
        """Check if order item is cancelled"""
        return self.state == "Cancelled"

    def can_be_cancelled(self) -> bool:
        """Check if order item can be cancelled"""
        return self.state in ["Added", "Confirmed"]

    def to_api_response(self) -> dict:
        """Convert to API response format"""
        data = self.model_dump()
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
