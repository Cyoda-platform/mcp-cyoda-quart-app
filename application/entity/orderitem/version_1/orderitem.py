"""
OrderItem Entity for Purrfect Pets API

Represents individual items within an order as specified in functional requirements.
"""

from decimal import Decimal
from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class OrderItem(CyodaEntity):
    """
    OrderItem entity represents individual items within an order.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: PENDING, CONFIRMED, DELIVERED, CANCELLED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "OrderItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the order item")
    order_id: int = Field(
        ...,
        alias="orderId",
        description="ID of the order this item belongs to (required)",
    )
    pet_id: int = Field(
        ..., alias="petId", description="ID of the pet being ordered (required)"
    )

    # Optional fields
    quantity: int = Field(
        default=1, description="Quantity of the pet (usually 1 for pets)"
    )
    unit_price: Optional[Decimal] = Field(
        None, alias="unitPrice", description="Price per unit at the time of order"
    )
    total_price: Optional[Decimal] = Field(
        None,
        alias="totalPrice",
        description="Total price for this item (quantity * unitPrice)",
    )

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, v: int) -> int:
        """Validate order_id field"""
        if v <= 0:
            raise ValueError("Order ID must be positive")
        return v

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate pet_id field"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity field"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @field_validator("unit_price")
    @classmethod
    def validate_unit_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate unit_price field"""
        if v is not None and v < 0:
            raise ValueError("Unit price cannot be negative")
        return v

    @field_validator("total_price")
    @classmethod
    def validate_total_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate total_price field"""
        if v is not None and v < 0:
            raise ValueError("Total price cannot be negative")
        return v

    def calculate_total_price(self) -> Optional[Decimal]:
        """Calculate total price based on quantity and unit price"""
        if self.unit_price is not None:
            return self.unit_price * self.quantity
        return None

    def is_pending(self) -> bool:
        """Check if order item is pending"""
        return self.state == "pending"

    def is_confirmed(self) -> bool:
        """Check if order item is confirmed"""
        return self.state == "confirmed"

    def is_delivered(self) -> bool:
        """Check if order item is delivered"""
        return self.state == "delivered"

    def is_cancelled(self) -> bool:
        """Check if order item is cancelled"""
        return self.state == "cancelled"

    def get_status(self) -> str:
        """Get order item status based on state"""
        state_mapping = {
            "pending": "PENDING",
            "confirmed": "CONFIRMED",
            "delivered": "DELIVERED",
            "cancelled": "CANCELLED",
        }
        return state_mapping.get(self.state, "UNKNOWN")
