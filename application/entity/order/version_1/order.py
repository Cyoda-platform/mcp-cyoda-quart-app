"""
Order Entity for Purrfect Pets API Application

Represents a purchase order for pets in the pet store.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity represents a purchase order in the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> validated -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from Petstore API
    pet_id: str = Field(..., alias="petId", description="ID of the pet being ordered")
    quantity: int = Field(default=1, description="Quantity of pets ordered")

    # Optional fields
    ship_date: Optional[str] = Field(
        default=None,
        alias="shipDate",
        description="Shipping date for the order"
    )
    status: Optional[str] = Field(
        default="placed",
        description="Order status"
    )
    complete: Optional[bool] = Field(
        default=False,
        description="Whether the order is complete"
    )

    # Additional fields for enhanced functionality
    customer_email: Optional[str] = Field(
        default=None,
        alias="customerEmail",
        description="Customer email address"
    )
    total_amount: Optional[float] = Field(
        default=None,
        alias="totalAmount",
        description="Total order amount"
    )
    shipping_address: Optional[str] = Field(
        default=None,
        alias="shippingAddress",
        description="Shipping address"
    )

    # Processing-related fields
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data populated during processing"
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="validationResult",
        description="Result of validation checks"
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = ["placed", "approved", "delivered"]

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: str) -> str:
        """Validate pet ID"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet ID must be non-empty")
        return v.strip()

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate order quantity"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        if v > 10:
            raise ValueError("Quantity cannot exceed 10 pets per order")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate order status"""
        if v is not None and v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("customer_email")
    @classmethod
    def validate_customer_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate customer email"""
        if v is not None:
            if "@" not in v or "." not in v:
                raise ValueError("Invalid email format")
            if len(v) > 100:
                raise ValueError("Email must be at most 100 characters long")
        return v

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate total amount"""
        if v is not None:
            if v < 0:
                raise ValueError("Total amount cannot be negative")
            if v > 1000000:
                raise ValueError("Total amount cannot exceed $1,000,000")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Order":
        """Validate business logic rules"""
        # If order is complete, it must have a ship date
        if self.complete and not self.ship_date:
            raise ValueError("Complete orders must have a ship date")
        
        # If status is delivered, order must be complete
        if self.status == "delivered" and not self.complete:
            raise ValueError("Delivered orders must be marked as complete")
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def set_validation_result(self, validation_result: Dict[str, Any]) -> None:
        """Set validation result and update timestamp"""
        self.validation_result = validation_result
        self.update_timestamp()

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.status == "placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.status == "approved"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.status == "delivered"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
