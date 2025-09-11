"""
Order Entity for Purrfect Pets API

Represents an order placed by a customer as specified in functional requirements.
"""

from datetime import datetime
from decimal import Decimal
from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Address(CyodaEntity):
    """Address reference for Order entity"""

    ENTITY_NAME: ClassVar[str] = "Address"
    ENTITY_VERSION: ClassVar[int] = 1

    id: Optional[int] = Field(None, description="Address ID")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    zip_code: Optional[str] = Field(
        None, alias="zipCode", description="ZIP or postal code"
    )
    country: Optional[str] = Field(None, description="Country name")


class Order(CyodaEntity):
    """
    Order entity represents an order placed by a customer.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: PLACED, APPROVED, DELIVERED, CANCELLED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the order")
    user_id: int = Field(
        ...,
        alias="userId",
        description="ID of the user who placed the order (required)",
    )

    # Optional fields
    order_date: Optional[datetime] = Field(
        None, alias="orderDate", description="Date and time when the order was placed"
    )
    ship_date: Optional[datetime] = Field(
        None, alias="shipDate", description="Date when the order was shipped"
    )
    total_amount: Optional[Decimal] = Field(
        None, alias="totalAmount", description="Total amount of the order"
    )
    shipping_address: Optional[Address] = Field(
        None, alias="shippingAddress", description="Shipping address for the order"
    )
    payment_method: Optional[str] = Field(
        None, alias="paymentMethod", description="Payment method used"
    )
    notes: Optional[str] = Field(None, description="Additional notes for the order")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validate user_id field"""
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate total_amount field"""
        if v is not None and v < 0:
            raise ValueError("Total amount cannot be negative")
        return v

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.state == "placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.state == "approved"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.state == "delivered"

    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.state == "cancelled"

    def get_status(self) -> str:
        """Get order status based on state"""
        state_mapping = {
            "placed": "PLACED",
            "approved": "APPROVED",
            "delivered": "DELIVERED",
            "cancelled": "CANCELLED",
        }
        return state_mapping.get(self.state, "UNKNOWN")
