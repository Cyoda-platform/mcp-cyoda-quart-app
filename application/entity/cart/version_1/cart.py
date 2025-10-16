# entity/cart/version_1/cart.py

"""
Cart Entity for Cyoda OMS Application

Represents a shopping cart with status management, line items, totals calculation,
and guest contact information as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Cart(CyodaEntity):
    """
    Cart entity for shopping cart functionality.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    Status managed by workflow: NEW → ACTIVE → CHECKING_OUT → CONVERTED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Cart"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    cartId: str = Field(..., alias="cartId", description="Cart identifier")
    status: str = Field(..., description="Cart status: NEW, ACTIVE, CHECKING_OUT, CONVERTED")
    lines: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Cart line items with sku, name, price, qty"
    )
    totalItems: int = Field(
        default=0,
        alias="totalItems",
        description="Total number of items in cart"
    )
    grandTotal: float = Field(
        default=0.0,
        alias="grandTotal",
        description="Grand total amount"
    )

    # Optional guest contact information
    guestContact: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="guestContact",
        description="Guest contact information including name, email, phone, address"
    )

    # Timestamps
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the cart was created"
    )
    updatedAt: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the cart was last updated"
    )

    # Valid statuses
    VALID_STATUSES: ClassVar[List[str]] = ["NEW", "ACTIVE", "CHECKING_OUT", "CONVERTED"]

    @field_validator("cartId")
    @classmethod
    def validate_cart_id(cls, v: str) -> str:
        """Validate cart ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Cart ID must be non-empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {cls.VALID_STATUSES}")
        return v

    @field_validator("totalItems")
    @classmethod
    def validate_total_items(cls, v: int) -> int:
        """Validate total items field"""
        if v < 0:
            raise ValueError("Total items must be non-negative")
        return v

    @field_validator("grandTotal")
    @classmethod
    def validate_grand_total(cls, v: float) -> float:
        """Validate grand total field"""
        if v < 0:
            raise ValueError("Grand total must be non-negative")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Cart":
        """Validate business logic rules"""
        # Ensure totals match line items
        calculated_items = sum(line.get("qty", 0) for line in self.lines)
        calculated_total = sum(line.get("price", 0) * line.get("qty", 0) for line in self.lines)
        
        # Allow small floating point differences
        if abs(self.totalItems - calculated_items) > 0:
            self.totalItems = calculated_items
        
        if abs(self.grandTotal - calculated_total) > 0.01:
            self.grandTotal = round(calculated_total, 2)
        
        return self

    def update_timestamp(self) -> None:
        """Update the updatedAt timestamp to current time"""
        self.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add_line_item(self, sku: str, name: str, price: float, qty: int) -> None:
        """Add or update a line item in the cart"""
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price must be non-negative")

        # Find existing line item
        for line in self.lines:
            if line.get("sku") == sku:
                line["qty"] += qty
                self._recalculate_totals()
                self.update_timestamp()
                return

        # Add new line item
        self.lines.append({
            "sku": sku,
            "name": name,
            "price": price,
            "qty": qty
        })
        self._recalculate_totals()
        self.update_timestamp()

    def update_line_item(self, sku: str, qty: int) -> None:
        """Update quantity of existing line item or remove if qty is 0"""
        if qty < 0:
            raise ValueError("Quantity must be non-negative")

        for i, line in enumerate(self.lines):
            if line.get("sku") == sku:
                if qty == 0:
                    # Remove line item
                    self.lines.pop(i)
                else:
                    # Update quantity
                    line["qty"] = qty
                self._recalculate_totals()
                self.update_timestamp()
                return

        if qty > 0:
            raise ValueError(f"Line item with SKU {sku} not found in cart")

    def remove_line_item(self, sku: str) -> None:
        """Remove a line item from the cart"""
        for i, line in enumerate(self.lines):
            if line.get("sku") == sku:
                self.lines.pop(i)
                self._recalculate_totals()
                self.update_timestamp()
                return
        raise ValueError(f"Line item with SKU {sku} not found in cart")

    def _recalculate_totals(self) -> None:
        """Recalculate total items and grand total"""
        self.totalItems = sum(line.get("qty", 0) for line in self.lines)
        self.grandTotal = round(sum(line.get("price", 0) * line.get("qty", 0) for line in self.lines), 2)

    def clear_cart(self) -> None:
        """Clear all line items from the cart"""
        self.lines = []
        self.totalItems = 0
        self.grandTotal = 0.0
        self.update_timestamp()

    def set_guest_contact(self, guest_contact: Dict[str, Any]) -> None:
        """Set guest contact information"""
        self.guestContact = guest_contact
        self.update_timestamp()

    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.lines) == 0

    def get_line_item(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get line item by SKU"""
        for line in self.lines:
            if line.get("sku") == sku:
                return line
        return None

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
