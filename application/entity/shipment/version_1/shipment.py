# entity/shipment/version_1/shipment.py

"""
Shipment Entity for Cyoda OMS Application

Represents a shipment for shipping management with status tracking
and line items as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Shipment(CyodaEntity):
    """
    Shipment entity for shipping management.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    Status managed by workflow: PICKING → WAITING_TO_SEND → SENT → DELIVERED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Shipment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    shipmentId: str = Field(..., alias="shipmentId", description="Shipment identifier")
    orderId: str = Field(..., alias="orderId", description="Associated order identifier")
    status: str = Field(..., description="Shipment status: PICKING, WAITING_TO_SEND, SENT, DELIVERED")
    lines: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Shipment line items with sku, qtyOrdered, qtyPicked, qtyShipped"
    )

    # Optional fields
    trackingNumber: Optional[str] = Field(
        default=None,
        alias="trackingNumber",
        description="Tracking number for the shipment"
    )
    carrier: Optional[str] = Field(
        default=None,
        description="Shipping carrier"
    )
    shippedAt: Optional[str] = Field(
        default=None,
        alias="shippedAt",
        description="Timestamp when shipment was sent"
    )
    deliveredAt: Optional[str] = Field(
        default=None,
        alias="deliveredAt",
        description="Timestamp when shipment was delivered"
    )

    # Timestamps
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the shipment was created"
    )
    updatedAt: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the shipment was last updated"
    )

    # Valid statuses
    VALID_STATUSES: ClassVar[List[str]] = ["PICKING", "WAITING_TO_SEND", "SENT", "DELIVERED"]

    @field_validator("shipmentId")
    @classmethod
    def validate_shipment_id(cls, v: str) -> str:
        """Validate shipment ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Shipment ID must be non-empty")
        return v.strip()

    @field_validator("orderId")
    @classmethod
    def validate_order_id(cls, v: str) -> str:
        """Validate order ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Order ID must be non-empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {cls.VALID_STATUSES}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Shipment":
        """Validate business logic rules"""
        # Validate line items quantities
        for line in self.lines:
            qty_ordered = line.get("qtyOrdered", 0)
            qty_picked = line.get("qtyPicked", 0)
            qty_shipped = line.get("qtyShipped", 0)
            
            if qty_picked > qty_ordered:
                raise ValueError(f"Picked quantity ({qty_picked}) cannot exceed ordered quantity ({qty_ordered}) for SKU {line.get('sku')}")
            
            if qty_shipped > qty_picked:
                raise ValueError(f"Shipped quantity ({qty_shipped}) cannot exceed picked quantity ({qty_picked}) for SKU {line.get('sku')}")
        
        return self

    def update_timestamp(self) -> None:
        """Update the updatedAt timestamp to current time"""
        self.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add_line_item(self, sku: str, qty_ordered: int) -> None:
        """Add a line item to the shipment"""
        if qty_ordered <= 0:
            raise ValueError("Ordered quantity must be positive")

        self.lines.append({
            "sku": sku,
            "qtyOrdered": qty_ordered,
            "qtyPicked": 0,
            "qtyShipped": 0
        })
        self.update_timestamp()

    def update_picked_quantity(self, sku: str, qty_picked: int) -> None:
        """Update picked quantity for a line item"""
        if qty_picked < 0:
            raise ValueError("Picked quantity must be non-negative")

        for line in self.lines:
            if line.get("sku") == sku:
                if qty_picked > line.get("qtyOrdered", 0):
                    raise ValueError(f"Picked quantity ({qty_picked}) cannot exceed ordered quantity ({line.get('qtyOrdered', 0)})")
                line["qtyPicked"] = qty_picked
                self.update_timestamp()
                return

        raise ValueError(f"Line item with SKU {sku} not found in shipment")

    def update_shipped_quantity(self, sku: str, qty_shipped: int) -> None:
        """Update shipped quantity for a line item"""
        if qty_shipped < 0:
            raise ValueError("Shipped quantity must be non-negative")

        for line in self.lines:
            if line.get("sku") == sku:
                if qty_shipped > line.get("qtyPicked", 0):
                    raise ValueError(f"Shipped quantity ({qty_shipped}) cannot exceed picked quantity ({line.get('qtyPicked', 0)})")
                line["qtyShipped"] = qty_shipped
                self.update_timestamp()
                return

        raise ValueError(f"Line item with SKU {sku} not found in shipment")

    def mark_shipped(self, tracking_number: Optional[str] = None, carrier: Optional[str] = None) -> None:
        """Mark shipment as shipped"""
        if self.status != "WAITING_TO_SEND":
            raise ValueError(f"Cannot mark shipment as shipped from status: {self.status}")
        
        self.status = "SENT"
        self.shippedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if tracking_number:
            self.trackingNumber = tracking_number
        if carrier:
            self.carrier = carrier
        self.update_timestamp()

    def mark_delivered(self) -> None:
        """Mark shipment as delivered"""
        if self.status != "SENT":
            raise ValueError(f"Cannot mark shipment as delivered from status: {self.status}")
        
        self.status = "DELIVERED"
        self.deliveredAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_fully_picked(self) -> bool:
        """Check if all items are fully picked"""
        for line in self.lines:
            if line.get("qtyPicked", 0) < line.get("qtyOrdered", 0):
                return False
        return True

    def is_fully_shipped(self) -> bool:
        """Check if all items are fully shipped"""
        for line in self.lines:
            if line.get("qtyShipped", 0) < line.get("qtyPicked", 0):
                return False
        return True

    def is_delivered(self) -> bool:
        """Check if shipment is delivered"""
        return self.status == "DELIVERED"

    def get_line_item(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get line item by SKU"""
        for line in self.lines:
            if line.get("sku") == sku:
                return line
        return None

    def get_total_ordered_items(self) -> int:
        """Get total number of ordered items"""
        return sum(line.get("qtyOrdered", 0) for line in self.lines)

    def get_total_picked_items(self) -> int:
        """Get total number of picked items"""
        return sum(line.get("qtyPicked", 0) for line in self.lines)

    def get_total_shipped_items(self) -> int:
        """Get total number of shipped items"""
        return sum(line.get("qtyShipped", 0) for line in self.lines)

    @classmethod
    def create_from_order(cls, shipment_id: str, order_data: Dict[str, Any]) -> "Shipment":
        """Create shipment from order data"""
        shipment_lines = []
        for order_line in order_data.get("lines", []):
            shipment_lines.append({
                "sku": order_line.get("sku"),
                "qtyOrdered": order_line.get("qty", 0),
                "qtyPicked": 0,
                "qtyShipped": 0
            })

        return cls(
            shipmentId=shipment_id,
            orderId=order_data.get("orderId"),
            status="PICKING",
            lines=shipment_lines
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
