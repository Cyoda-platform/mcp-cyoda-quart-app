"""
Order Entity for Purrfect Pets API

Represents purchase orders for pets in the Purrfect Pets store with comprehensive
validation and workflow state management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity represents purchase orders for pets in the Purrfect Pets store.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> placed -> approved -> delivered
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    petId: str = Field(
        ..., alias="petId", description="Reference to the pet being ordered"
    )
    userId: str = Field(
        ..., alias="userId", description="Reference to the user placing the order"
    )

    # Optional fields with defaults
    quantity: int = Field(default=1, description="Number of pets ordered", ge=1)
    shipDate: Optional[str] = Field(
        default=None,
        alias="shipDate",
        description="Expected shipping date (ISO 8601 format)",
    )
    complete: bool = Field(default=False, description="Whether the order is complete")
    totalAmount: Optional[float] = Field(
        default=None,
        alias="totalAmount",
        description="Total order amount in USD",
        ge=0.0,
    )
    shippingAddress: Optional[Dict[str, Any]] = Field(
        default=None, alias="shippingAddress", description="Delivery address details"
    )

    # Processing-related fields (populated during processing)
    orderDate: Optional[str] = Field(
        default=None, alias="orderDate", description="Date when order was placed"
    )
    estimatedDelivery: Optional[str] = Field(
        default=None, alias="estimatedDelivery", description="Estimated delivery date"
    )
    approvedAt: Optional[str] = Field(
        default=None,
        alias="approvedAt",
        description="Timestamp when order was approved",
    )
    trackingNumber: Optional[str] = Field(
        default=None, alias="trackingNumber", description="Shipping tracking number"
    )
    deliveredAt: Optional[str] = Field(
        default=None,
        alias="deliveredAt",
        description="Timestamp when order was delivered",
    )

    @field_validator("petId")
    @classmethod
    def validate_pet_id(cls, v: str) -> str:
        """Validate pet ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet ID is required")
        return v.strip()

    @field_validator("userId")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID is required")
        return v.strip()

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity field"""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        if v > 10:  # Reasonable limit for pet orders
            raise ValueError("Quantity cannot exceed 10 pets per order")
        return v

    @field_validator("totalAmount")
    @classmethod
    def validate_total_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate total amount field"""
        if v is not None and v < 0:
            raise ValueError("Total amount cannot be negative")
        return v

    @field_validator("shippingAddress")
    @classmethod
    def validate_shipping_address(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate shipping address structure"""
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError("Shipping address must be a dictionary")

        # Check for required address fields
        required_fields = ["street", "city", "state", "zipCode"]
        for field in required_fields:
            if field not in v or not v[field] or len(str(v[field]).strip()) == 0:
                raise ValueError(f"Shipping address must include {field}")

        return v

    @field_validator(
        "shipDate", "orderDate", "estimatedDelivery", "approvedAt", "deliveredAt"
    )
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (ISO 8601)"""
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError("Date must be a string in ISO 8601 format")

        # Basic ISO 8601 format validation
        try:
            # Try to parse the date to validate format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                "Date must be in ISO 8601 format (e.g., '2023-12-25T10:30:00Z')"
            )

        return v

    @field_validator("trackingNumber")
    @classmethod
    def validate_tracking_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate tracking number format"""
        if v is None:
            return v

        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Tracking number must be a non-empty string")

        # Basic tracking number validation (alphanumeric, 6-20 characters)
        cleaned = v.strip().upper()
        if not cleaned.isalnum() or len(cleaned) < 6 or len(cleaned) > 20:
            raise ValueError("Tracking number must be 6-20 alphanumeric characters")

        return cleaned

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Order":
        """Validate business logic rules"""
        # Ensure complete flag is consistent with state
        if self.state == "delivered" and not self.complete:
            self.complete = True

        # Ensure delivered orders have delivery timestamp
        if self.state == "delivered" and not self.deliveredAt:
            # This will be set by the processor, so we don't enforce it here
            pass

        # Ensure approved orders have approval timestamp
        if self.state in ["approved", "delivered"] and not self.approvedAt:
            # This will be set by the processor, so we don't enforce it here
            pass

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_placed(self) -> bool:
        """Check if order has been placed"""
        return self.state == "placed"

    def is_approved(self) -> bool:
        """Check if order has been approved"""
        return self.state == "approved"

    def is_delivered(self) -> bool:
        """Check if order has been delivered"""
        return self.state == "delivered"

    def is_cancelled(self) -> bool:
        """Check if order has been cancelled"""
        return self.state == "cancelled"

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
