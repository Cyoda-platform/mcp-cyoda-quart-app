"""
Order Entity for Purrfect Pets Application

Represents a customer order for pets with all required attributes
and relationships as specified in functional requirements.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity represents a customer order for pets.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> placed -> confirmed -> processing -> shipped -> delivered
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    user_id: int = Field(..., alias="userId", description="ID of the user who placed the order")
    pet_id: int = Field(..., alias="petId", description="ID of the pet being ordered")

    # Order details
    quantity: Optional[int] = Field(default=1, description="Quantity of pets ordered")
    total_amount: Optional[Decimal] = Field(None, alias="totalAmount", description="Total amount for the order")
    order_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="orderDate",
        description="When the order was placed"
    )
    ship_date: Optional[str] = Field(None, alias="shipDate", description="When the order was shipped")
    delivery_address: Optional[str] = Field(None, alias="deliveryAddress", description="Delivery address for the order")
    special_instructions: Optional[str] = Field(None, alias="specialInstructions", description="Special instructions for the order")
    payment_method: Optional[str] = Field(None, alias="paymentMethod", description="Payment method used")
    tracking_number: Optional[str] = Field(None, alias="trackingNumber", description="Shipping tracking number")

    # Audit timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="When the order was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="When the order was last updated"
    )

    # Validation constants
    VALID_PAYMENT_METHODS: ClassVar[list[str]] = ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL", "BANK_TRANSFER", "CASH"]
    MIN_QUANTITY: ClassVar[int] = 1
    MAX_QUANTITY: ClassVar[int] = 10

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: int) -> int:
        """Validate user ID"""
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate pet ID"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> Optional[int]:
        """Validate order quantity"""
        if v is not None:
            if v < cls.MIN_QUANTITY:
                raise ValueError(f"Quantity must be at least {cls.MIN_QUANTITY}")
            if v > cls.MAX_QUANTITY:
                raise ValueError(f"Quantity cannot exceed {cls.MAX_QUANTITY}")
        return v

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate total amount"""
        if v is not None:
            if v <= 0:
                raise ValueError("Total amount must be positive")
            if v > Decimal("999999.99"):
                raise ValueError("Total amount cannot exceed 999,999.99")
        return v

    @field_validator("delivery_address")
    @classmethod
    def validate_delivery_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate delivery address"""
        if v is not None:
            if len(v.strip()) < 10:
                raise ValueError("Delivery address must be at least 10 characters long")
            if len(v) > 500:
                raise ValueError("Delivery address must be at most 500 characters long")
            return v.strip()
        return v

    @field_validator("special_instructions")
    @classmethod
    def validate_special_instructions(cls, v: Optional[str]) -> Optional[str]:
        """Validate special instructions"""
        if v is not None:
            if len(v) > 1000:
                raise ValueError("Special instructions must be at most 1000 characters long")
            return v.strip() if v.strip() else None
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: Optional[str]) -> Optional[str]:
        """Validate payment method"""
        if v is not None:
            if v not in cls.VALID_PAYMENT_METHODS:
                raise ValueError(f"Payment method must be one of: {cls.VALID_PAYMENT_METHODS}")
        return v

    @field_validator("tracking_number")
    @classmethod
    def validate_tracking_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate tracking number"""
        if v is not None:
            if len(v.strip()) < 5:
                raise ValueError("Tracking number must be at least 5 characters long")
            if len(v) > 50:
                raise ValueError("Tracking number must be at most 50 characters long")
            return v.strip()
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.state == "placed"

    def is_confirmed(self) -> bool:
        """Check if order is confirmed"""
        return self.state == "confirmed"

    def is_processing(self) -> bool:
        """Check if order is processing"""
        return self.state == "processing"

    def is_shipped(self) -> bool:
        """Check if order is shipped"""
        return self.state == "shipped"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.state == "delivered"

    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.state == "cancelled"

    def is_returned(self) -> bool:
        """Check if order is returned"""
        return self.state == "returned"

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
