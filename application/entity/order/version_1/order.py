"""
Order Entity for Purrfect Pets API

Represents a purchase order for adopting/buying pets.
The Order entity uses workflow states managed by the system.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order represents a purchase order for adopting/buying pets.
    
    The Order entity uses `status` semantically as its state, which will be managed 
    by the system as `entity.meta.state`. The possible states are:
    - `placed`: Order has been placed
    - `approved`: Order has been approved
    - `delivered`: Pet has been delivered/picked up
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    petId: int = Field(..., alias="petId", description="ID of the pet being ordered")
    quantity: int = Field(default=1, description="Quantity of pets (usually 1)")
    customerName: str = Field(..., alias="customerName", description="Name of the customer")
    customerEmail: str = Field(..., alias="customerEmail", description="Email of the customer")
    customerPhone: str = Field(..., alias="customerPhone", description="Phone number of the customer")
    customerAddress: str = Field(..., alias="customerAddress", description="Address of the customer")
    totalAmount: Decimal = Field(..., alias="totalAmount", description="Total amount for the order")
    paymentMethod: str = Field(..., alias="paymentMethod", description="Payment method used")
    
    # Optional fields
    shipDate: Optional[str] = Field(default=None, alias="shipDate", description="Expected delivery/pickup date")
    notes: Optional[str] = Field(default=None, description="Additional notes for the order")
    
    # Processing-related fields (populated during processing)
    orderDate: Optional[str] = Field(default=None, alias="orderDate", description="Date when order was placed")
    approvedDate: Optional[str] = Field(default=None, alias="approvedDate", description="Date when order was approved")
    approvedBy: Optional[str] = Field(default=None, alias="approvedBy", description="Who approved the order")
    deliveredDate: Optional[str] = Field(default=None, alias="deliveredDate", description="Date when order was delivered")
    deliveredBy: Optional[str] = Field(default=None, alias="deliveredBy", description="Who delivered the order")
    deliverySignature: Optional[str] = Field(default=None, alias="deliverySignature", description="Delivery signature")

    @field_validator("petId")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate petId field"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity field"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        if v > 1:
            raise ValueError("Quantity cannot exceed 1 for pet orders")
        return v

    @field_validator("customerName")
    @classmethod
    def validate_customer_name(cls, v: str) -> str:
        """Validate customerName field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Customer name must be non-empty")
        if len(v) < 2:
            raise ValueError("Customer name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Customer name must be at most 100 characters long")
        return v.strip()

    @field_validator("customerEmail")
    @classmethod
    def validate_customer_email(cls, v: str) -> str:
        """Validate customerEmail field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Customer email must be non-empty")
        if "@" not in v:
            raise ValueError("Customer email must be valid")
        return v.strip().lower()

    @field_validator("customerPhone")
    @classmethod
    def validate_customer_phone(cls, v: str) -> str:
        """Validate customerPhone field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Customer phone must be non-empty")
        return v.strip()

    @field_validator("customerAddress")
    @classmethod
    def validate_customer_address(cls, v: str) -> str:
        """Validate customerAddress field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Customer address must be non-empty")
        if len(v) > 500:
            raise ValueError("Customer address must be at most 500 characters long")
        return v.strip()

    @field_validator("totalAmount")
    @classmethod
    def validate_total_amount(cls, v: Decimal) -> Decimal:
        """Validate totalAmount field"""
        if v < 0:
            raise ValueError("Total amount must be non-negative")
        return v

    @field_validator("paymentMethod")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        """Validate paymentMethod field"""
        allowed_methods = ["credit_card", "debit_card", "cash", "bank_transfer"]
        if v not in allowed_methods:
            raise ValueError(f"Payment method must be one of: {allowed_methods}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Order":
        """Validate business logic rules"""
        # Additional business validation can be added here
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_placed(self) -> bool:
        """Check if order is in placed state"""
        return self.state == "placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.state == "approved"

    def is_delivered(self) -> bool:
        """Check if order has been delivered"""
        return self.state == "delivered"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
