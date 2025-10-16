# entity/order/version_1/order.py

"""
Order Entity for Cyoda OMS Application

Represents an order with lifecycle management and order number generation
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """
    Order entity for order lifecycle management.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    Status managed by workflow: WAITING_TO_FULFILL → PICKING → WAITING_TO_SEND → SENT → DELIVERED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    orderId: str = Field(..., alias="orderId", description="Order identifier")
    orderNumber: str = Field(..., alias="orderNumber", description="Short ULID order number")
    status: str = Field(..., description="Order status")
    lines: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Order line items with sku, name, unitPrice, qty, lineTotal"
    )
    totals: Dict[str, float] = Field(
        default_factory=dict,
        description="Order totals with items and grand total"
    )
    guestContact: Dict[str, Any] = Field(
        ...,
        alias="guestContact",
        description="Guest contact information including name, email, phone, address"
    )

    # Optional fields
    paymentId: Optional[str] = Field(
        default=None,
        alias="paymentId",
        description="Associated payment identifier"
    )
    cartId: Optional[str] = Field(
        default=None,
        alias="cartId",
        description="Source cart identifier"
    )

    # Timestamps
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the order was created"
    )
    updatedAt: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the order was last updated"
    )

    # Valid statuses
    VALID_STATUSES: ClassVar[List[str]] = [
        "WAITING_TO_FULFILL", "PICKING", "WAITING_TO_SEND", "SENT", "DELIVERED"
    ]

    @field_validator("orderId")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Validate order ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Order ID must be non-empty")
        return v.strip()

    @field_validator("orderNumber")
    @classmethod
    def validate_order_number(cls, v: str) -> str:
        """Validate order number field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Order number must be non-empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {cls.VALID_STATUSES}")
        return v

    @field_validator("guestContact")
    @classmethod
    def validate_guest_contact(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate guest contact information"""
        if not v:
            raise ValueError("Guest contact information is required")
        
        # Validate required fields
        if not v.get("name"):
            raise ValueError("Guest contact name is required")
        
        address = v.get("address", {})
        if not address:
            raise ValueError("Guest contact address is required")
        
        required_address_fields = ["line1", "city", "postcode", "country"]
        for field in required_address_fields:
            if not address.get(field):
                raise ValueError(f"Guest contact address {field} is required")
        
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Order":
        """Validate business logic rules"""
        # Ensure totals are calculated correctly
        if self.lines:
            calculated_items_total = sum(line.get("lineTotal", 0) for line in self.lines)
            if "items" not in self.totals:
                self.totals["items"] = calculated_items_total
            if "grand" not in self.totals:
                self.totals["grand"] = calculated_items_total
        
        return self

    def update_timestamp(self) -> None:
        """Update the updatedAt timestamp to current time"""
        self.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add_line_item(self, sku: str, name: str, unit_price: float, qty: int) -> None:
        """Add a line item to the order"""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price < 0:
            raise ValueError("Unit price must be non-negative")

        line_total = round(unit_price * qty, 2)
        self.lines.append({
            "sku": sku,
            "name": name,
            "unitPrice": unit_price,
            "qty": qty,
            "lineTotal": line_total
        })
        self._recalculate_totals()
        self.update_timestamp()

    def _recalculate_totals(self) -> None:
        """Recalculate order totals"""
        items_total = sum(line.get("lineTotal", 0) for line in self.lines)
        self.totals = {
            "items": round(items_total, 2),
            "grand": round(items_total, 2)  # For demo, grand total equals items total
        }

    def set_guest_contact(self, guest_contact: Dict[str, Any]) -> None:
        """Set guest contact information"""
        self.guestContact = guest_contact
        self.update_timestamp()

    def get_total_items_count(self) -> int:
        """Get total number of items in the order"""
        return sum(line.get("qty", 0) for line in self.lines)

    def get_line_item(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get line item by SKU"""
        for line in self.lines:
            if line.get("sku") == sku:
                return line
        return None

    def is_fulfilled(self) -> bool:
        """Check if order is fulfilled (SENT or DELIVERED)"""
        return self.status in ["SENT", "DELIVERED"]

    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.status == "DELIVERED"

    def can_be_canceled(self) -> bool:
        """Check if order can be canceled (not yet sent)"""
        return self.status in ["WAITING_TO_FULFILL", "PICKING", "WAITING_TO_SEND"]

    @classmethod
    def create_from_cart_and_payment(
        cls,
        order_id: str,
        order_number: str,
        cart_data: Dict[str, Any],
        payment_data: Dict[str, Any]
    ) -> "Order":
        """Create order from cart and payment data"""
        # Convert cart lines to order lines
        order_lines = []
        for cart_line in cart_data.get("lines", []):
            order_lines.append({
                "sku": cart_line.get("sku"),
                "name": cart_line.get("name"),
                "unitPrice": cart_line.get("price"),
                "qty": cart_line.get("qty"),
                "lineTotal": round(cart_line.get("price", 0) * cart_line.get("qty", 0), 2)
            })

        # Calculate totals
        items_total = sum(line["lineTotal"] for line in order_lines)
        totals = {
            "items": round(items_total, 2),
            "grand": round(items_total, 2)
        }

        return cls(
            orderId=order_id,
            orderNumber=order_number,
            status="WAITING_TO_FULFILL",
            lines=order_lines,
            totals=totals,
            guestContact=cart_data.get("guestContact", {}),
            paymentId=payment_data.get("paymentId"),
            cartId=cart_data.get("cartId")
        )

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
