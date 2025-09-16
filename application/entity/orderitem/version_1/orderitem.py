"""
OrderItem Entity for Purrfect Pets API

Represents an item within an order as specified in the functional requirements.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class OrderItem(CyodaEntity):
    """
    OrderItem entity representing items within an order.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending -> confirmed -> shipped
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "OrderItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    order_id: int = Field(..., description="Foreign Key to Order")
    pet_id: int = Field(..., description="Foreign Key to Pet")
    quantity: int = Field(default=1, description="Quantity of pets ordered", ge=1)
    unit_price: float = Field(..., description="Price per pet at time of order", gt=0)
    total_price: float = Field(..., description="quantity * unit_price", ge=0)

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the order item was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the order item was last updated (ISO 8601 format)",
    )

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity field"""
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: float) -> float:
        """Validate unit_price field"""
        if v <= 0:
            raise ValueError("Unit price must be greater than 0")
        return v

    @model_validator(mode="after")
    def validate_total_price(self) -> "OrderItem":
        """Validate that total_price equals quantity * unit_price"""
        expected_total = self.quantity * self.unit_price
        if abs(self.total_price - expected_total) > 0.01:  # Allow for small floating point differences
            raise ValueError(f"Total price must equal quantity * unit_price (expected {expected_total}, got {self.total_price})")
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def calculate_total_price(self) -> None:
        """Calculate and set total_price based on quantity and unit_price"""
        self.total_price = self.quantity * self.unit_price
        self.update_timestamp()

    def is_pending(self) -> bool:
        """Check if order item is pending"""
        return self.state == "pending"

    def is_confirmed(self) -> bool:
        """Check if order item is confirmed"""
        return self.state == "confirmed"

    def is_shipped(self) -> bool:
        """Check if order item is shipped"""
        return self.state == "shipped"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
