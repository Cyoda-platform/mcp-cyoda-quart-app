# entity/order/version_1/order.py

"""
Order Entity for Cyoda Client Application

Represents a pet purchase order in the Purrfect Pets store.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order represents a pet purchase order in the Purrfect Pets store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> placed -> approved -> delivered
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    pet_id: str = Field(..., alias="petId", description="Reference to the pet being ordered")
    user_id: str = Field(..., alias="userId", description="Reference to the user placing the order")
    
    # Optional fields with defaults
    quantity: int = Field(default=1, description="Number of pets ordered")
    ship_date: Optional[str] = Field(
        default=None,
        alias="shipDate",
        description="Expected shipping date (ISO date)"
    )
    total_amount: Optional[float] = Field(
        default=None,
        alias="totalAmount",
        description="Total order amount"
    )
    
    # Processing-related fields (populated during processing)
    placed_date: Optional[str] = Field(
        default=None,
        alias="placedDate",
        description="Date when order was placed"
    )
    approved_date: Optional[str] = Field(
        default=None,
        alias="approvedDate",
        description="Date when order was approved"
    )
    delivered_date: Optional[str] = Field(
        default=None,
        alias="deliveredDate",
        description="Date when order was delivered"
    )
    last_updated: Optional[str] = Field(
        default=None,
        alias="lastUpdated",
        description="Last update timestamp"
    )

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: str) -> str:
        """Validate pet_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet ID must be non-empty")
        return v.strip()

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID must be non-empty")
        return v.strip()

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity field"""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        if v > 100:
            raise ValueError("Quantity must be at most 100")
        return v

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate total_amount field"""
        if v is not None and v < 0:
            raise ValueError("Total amount must be non-negative")
        return v

    @field_validator("ship_date")
    @classmethod
    def validate_ship_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate ship_date field"""
        if v is None:
            return None
        # Basic validation - ensure it's not empty
        if len(v.strip()) == 0:
            return None
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the last_updated timestamp to current time"""
        self.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_placed_date(self) -> None:
        """Set placed date and update timestamp"""
        self.placed_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_approved_date(self) -> None:
        """Set approved date and update timestamp"""
        self.approved_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_delivered_date(self) -> None:
        """Set delivered date and update timestamp"""
        self.delivered_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_placed(self) -> bool:
        """Check if order is placed"""
        return self.state == "placed"

    def is_approved(self) -> bool:
        """Check if order is approved"""
        return self.state == "approved"

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.state == "delivered"

    def calculate_total(self, unit_price: float) -> None:
        """Calculate total amount based on quantity and unit price"""
        self.total_amount = self.quantity * unit_price
        self.update_timestamp()

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["meta"] = {"state": self.state}
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
