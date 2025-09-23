"""
Store Entity for Product Performance Analysis and Reporting System

Represents store information and inventory data from the Pet Store API.
Extends CyodaEntity to integrate with Cyoda workflow system.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Store(CyodaEntity):
    """
    Store entity representing store information and inventory data.

    This entity stores store-related data from the Pet Store API
    and is used for performance analysis and reporting.

    Inherits from CyodaEntity to get workflow management capabilities.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Store"
    ENTITY_VERSION: ClassVar[int] = 1

    # Store identification
    store_name: str = Field(..., alias="storeName", description="Name of the store")
    store_id: Optional[str] = Field(
        None, alias="storeId", description="Unique store identifier"
    )

    # Store contact information
    address: Optional[str] = Field(None, description="Store address")
    phone: Optional[str] = Field(None, description="Store phone number")
    email: Optional[str] = Field(None, description="Store email address")

    # Inventory data from Pet Store API
    inventory_data: Optional[Dict[str, int]] = Field(
        None,
        alias="inventoryData",
        description="Inventory counts by status (available, pending, sold)",
    )
    last_inventory_update: Optional[str] = Field(
        None,
        alias="lastInventoryUpdate",
        description="Timestamp when inventory was last updated",
    )

    # Performance metrics
    total_pets: Optional[int] = Field(
        None, alias="totalPets", description="Total number of pets in store"
    )
    available_pets: Optional[int] = Field(
        None, alias="availablePets", description="Number of available pets"
    )
    pending_pets: Optional[int] = Field(
        None, alias="pendingPets", description="Number of pending pets"
    )
    sold_pets: Optional[int] = Field(
        None, alias="soldPets", description="Number of sold pets"
    )

    # Analysis results
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        alias="performanceMetrics",
        description="Store performance analysis results",
    )
    last_analyzed_at: Optional[str] = Field(
        None,
        alias="lastAnalyzedAt",
        description="Timestamp when store analysis was last run",
    )

    @field_validator("store_name")
    @classmethod
    def validate_store_name(cls, v: str) -> str:
        """Validate store name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store name must be non-empty")
        if len(v) > 255:
            raise ValueError("Store name must be at most 255 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Basic email validation"""
        if v is not None and v.strip():
            if "@" not in v or "." not in v:
                raise ValueError("Invalid email format")
            return v.strip()
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Basic phone validation"""
        if v is not None and v.strip():
            # Remove common phone formatting characters
            cleaned = "".join(c for c in v if c.isdigit() or c in "+()-. ")
            if (
                len(
                    cleaned.replace(" ", "")
                    .replace("-", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("+", "")
                    .replace(".", "")
                )
                < 10
            ):
                raise ValueError("Phone number must have at least 10 digits")
            return cleaned.strip()
        return v

    def update_inventory(self, inventory_data: Dict[str, int]) -> None:
        """Update inventory data and calculate totals"""
        self.inventory_data = inventory_data
        self.last_inventory_update = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Calculate totals
        self.available_pets = inventory_data.get("available", 0)
        self.pending_pets = inventory_data.get("pending", 0)
        self.sold_pets = inventory_data.get("sold", 0)
        self.total_pets = self.available_pets + self.pending_pets + self.sold_pets

        self.update_timestamp()

    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update performance metrics and timestamp"""
        self.performance_metrics = metrics
        self.last_analyzed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def get_availability_rate(self) -> Optional[float]:
        """Calculate availability rate as percentage"""
        if self.total_pets and self.total_pets > 0:
            return (self.available_pets or 0) / self.total_pets * 100.0
        return None

    def get_sales_rate(self) -> Optional[float]:
        """Calculate sales rate as percentage"""
        if self.total_pets and self.total_pets > 0:
            return (self.sold_pets or 0) / self.total_pets * 100.0
        return None

    def is_inventory_current(self, max_age_hours: int = 24) -> bool:
        """Check if inventory data is current within specified hours"""
        if not self.last_inventory_update:
            return False

        try:
            last_update = datetime.fromisoformat(
                self.last_inventory_update.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            age_hours = (now - last_update).total_seconds() / 3600
            return age_hours <= max_age_hours
        except (ValueError, AttributeError):
            return False

    def is_analyzed(self) -> bool:
        """Check if store has been analyzed"""
        return (
            self.performance_metrics is not None and self.last_analyzed_at is not None
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
