"""
Order Entity for Purrfect Pets API

Represents an order placed by a user as specified in the functional requirements.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity representing customer orders.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> placed -> approved -> shipped -> delivered/cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    user_id: int = Field(..., description="Foreign Key to User")
    order_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Order date (ISO 8601 format)",
    )
    ship_date: Optional[str] = Field(
        None, description="Estimated shipping date (ISO 8601 format)"
    )
    total_amount: float = Field(..., description="Total order amount", ge=0)
    shipping_address: str = Field(..., description="Shipping address", max_length=300)
    payment_method: str = Field(..., description="Payment method used")
    notes: Optional[str] = Field(None, description="Order notes", max_length=500)

    # Timestamps (inherited created_at from CyodaEntity)
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
        """Validate shipping_address field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Shipping address must be non-empty")
        if len(v) > 300:
            raise ValueError("Shipping address must be at most 300 characters long")
        return v.strip()

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        """Validate payment_method field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Payment method must be non-empty")
        return v.strip()

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        if len(v) > 500:
            raise ValueError("Order notes must be at most 500 characters long")
        return v.strip()

    @field_validator("ship_date")
    @classmethod
    def validate_ship_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate ship_date field"""
        if v is None:
            return None
        if len(v.strip()) == 0:
            return None
        # Basic ISO format validation could be added here
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.state == "placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.state == "approved"

    def is_shipped(self) -> bool:
        """Check if order is shipped"""
        return self.state == "shipped"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.state == "delivered"

    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.state == "cancelled"

    def set_ship_date(self, ship_date: str) -> None:
        """Set shipping date and update timestamp"""
        self.ship_date = ship_date
        self.update_timestamp()

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
