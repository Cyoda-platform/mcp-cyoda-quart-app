"""Order entity for Purrfect Pets API."""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import Field

from entity.cyoda_entity import CyodaEntity


class Order(CyodaEntity):
    """Order entity representing pet purchase orders."""

    ENTITY_NAME: ClassVar[str] = "Order"
    ENTITY_VERSION: ClassVar[int] = 1

    # Order-specific fields
    id: Optional[int] = Field(default=None, description="Order ID")
    ownerId: int = Field(..., description="Reference to owner")
    petId: int = Field(..., description="Reference to pet")
    quantity: int = Field(default=1, ge=1, description="Order quantity")
    totalAmount: float = Field(..., gt=0, description="Total order amount")
    orderDate: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Order date",
    )
    deliveryDate: Optional[str] = Field(
        default=None, description="Expected delivery date"
    )
    deliveryAddress: str = Field(..., description="Delivery address")
    notes: Optional[str] = Field(default=None, description="Special instructions")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp",
    )
    updatedAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp",
    )

    def __init__(self, **kwargs):
        """Initialize Order entity."""
        super().__init__(**kwargs)
        if self.state == "none":
            self.state = "initial_state"
