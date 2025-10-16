# entity/payment/version_1/payment.py

"""
Payment Entity for Cyoda OMS Application

Represents a payment with dummy processing functionality and auto-approval
after 3 seconds as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Payment(CyodaEntity):
    """
    Payment entity for dummy payment processing.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    Status managed by workflow: INITIATED → PAID/FAILED/CANCELED
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Payment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    paymentId: str = Field(..., alias="paymentId", description="Payment identifier")
    cartId: str = Field(..., alias="cartId", description="Associated cart identifier")
    amount: float = Field(..., description="Payment amount")
    status: str = Field(
        ..., description="Payment status: INITIATED, PAID, FAILED, CANCELED"
    )
    provider: str = Field(
        default="DUMMY", description="Payment provider (always DUMMY for demo)"
    )

    # Optional fields for payment processing
    initiatedAt: Optional[str] = Field(
        default=None,
        alias="initiatedAt",
        description="Timestamp when payment was initiated",
    )
    completedAt: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when payment was completed",
    )
    failureReason: Optional[str] = Field(
        default=None, alias="failureReason", description="Reason for payment failure"
    )

    # Timestamps
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the payment was created",
    )
    updatedAt: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the payment was last updated",
    )

    # Valid statuses
    VALID_STATUSES: ClassVar[List[str]] = ["INITIATED", "PAID", "FAILED", "CANCELED"]

    @field_validator("paymentId")
    @classmethod
    def validate_payment_id(cls, v: str) -> str:
        """Validate payment ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Payment ID must be non-empty")
        return v.strip()

    @field_validator("cartId")
    @classmethod
    def validate_cart_id(cls, v: str) -> str:
        """Validate cart ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Cart ID must be non-empty")
        return v.strip()

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount field"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {cls.VALID_STATUSES}")
        return v

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider field"""
        if v != "DUMMY":
            raise ValueError("Provider must be DUMMY for demo purposes")
        return v

    def update_timestamp(self) -> None:
        """Update the updatedAt timestamp to current time"""
        self.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_initiated(self) -> None:
        """Mark payment as initiated"""
        self.status = "INITIATED"
        self.initiatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_paid(self) -> None:
        """Mark payment as paid"""
        if self.status != "INITIATED":
            raise ValueError(f"Cannot mark payment as paid from status: {self.status}")
        self.status = "PAID"
        self.completedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_failed(self, reason: str) -> None:
        """Mark payment as failed with reason"""
        if self.status not in ["INITIATED"]:
            raise ValueError(
                f"Cannot mark payment as failed from status: {self.status}"
            )
        self.status = "FAILED"
        self.failureReason = reason
        self.completedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_canceled(self) -> None:
        """Mark payment as canceled"""
        if self.status not in ["INITIATED"]:
            raise ValueError(
                f"Cannot mark payment as canceled from status: {self.status}"
            )
        self.status = "CANCELED"
        self.completedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_completed(self) -> bool:
        """Check if payment is in a completed state"""
        return self.status in ["PAID", "FAILED", "CANCELED"]

    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == "PAID"

    def is_pending(self) -> bool:
        """Check if payment is still pending"""
        return self.status == "INITIATED"

    def get_processing_duration_seconds(self) -> Optional[float]:
        """Get processing duration in seconds if completed"""
        if not self.initiatedAt or not self.completedAt:
            return None

        try:
            initiated = datetime.fromisoformat(self.initiatedAt.replace("Z", "+00:00"))
            completed = datetime.fromisoformat(self.completedAt.replace("Z", "+00:00"))
            return (completed - initiated).total_seconds()
        except Exception:
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
