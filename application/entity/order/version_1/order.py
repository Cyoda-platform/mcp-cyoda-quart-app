"""
Order Entity for Purrfect Pets API

Represents an order placed by a user for purchasing pets.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity representing customer orders.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: Placed -> Approved -> Preparing -> Shipped -> Delivered -> Cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    user_id: int = Field(..., description="Foreign key to User")
    order_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Order date (auto-generated)",
    )
    ship_date: Optional[str] = Field(None, description="Shipping date")
    total_amount: float = Field(..., description="Total order amount", ge=0)
    shipping_address: str = Field(..., description="Shipping address", max_length=300)
    payment_method: str = Field(..., description="Payment method")
    notes: Optional[str] = Field(None, description="Order notes", max_length=500)

    # Timestamps (inherited from CyodaEntity but override for consistency)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the order was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the order was last updated (ISO 8601 format)",
    )

    @field_validator("shipping_address")
    @classmethod
    def validate_shipping_address(cls, v: str) -> str:
        """Validate shipping address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Shipping address must be non-empty")
        if len(v) > 300:
            raise ValueError("Shipping address must be at most 300 characters long")
        return v.strip()

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        """Validate payment method"""
        allowed_methods = ["CREDIT_CARD", "DEBIT_CARD", "CASH", "BANK_TRANSFER"]
        if v not in allowed_methods:
            raise ValueError(f"Payment method must be one of: {allowed_methods}")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate order notes"""
        if v is None:
            return v

        if len(v.strip()) == 0:
            return None

        if len(v) > 500:
            raise ValueError("Order notes must be at most 500 characters long")

        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_ship_date(self) -> None:
        """Set the ship date to current time"""
        self.ship_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.state == "Placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.state == "Approved"

    def is_preparing(self) -> bool:
        """Check if order is being prepared"""
        return self.state == "Preparing"

    def is_shipped(self) -> bool:
        """Check if order is shipped"""
        return self.state == "Shipped"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.state == "Delivered"

    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.state == "Cancelled"

    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self.state in ["Placed", "Approved", "Preparing"]

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
