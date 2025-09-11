# entity/emaildelivery/version_1/emaildelivery.py

"""
EmailDelivery Entity for Cyoda Client Application

Represents the delivery of a specific cat fact to a specific subscriber.
Manages the email delivery lifecycle from creation to confirmation.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailDelivery(CyodaEntity):
    """
    EmailDelivery represents the delivery of a specific cat fact to a specific subscriber.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> pending -> sent/failed -> delivered -> end
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailDelivery"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    subscriber_id: str = Field(
        ..., alias="subscriberId", description="Foreign key to Subscriber entity"
    )
    cat_fact_id: str = Field(
        ..., alias="catFactId", description="Foreign key to CatFact entity"
    )
    sent_date: Optional[str] = Field(
        default=None,
        alias="sentDate",
        description="Date and time when the email was sent (ISO 8601 format)",
    )
    delivery_attempts: int = Field(
        default=0,
        alias="deliveryAttempts",
        description="Number of delivery attempts made",
    )
    last_attempt_date: Optional[str] = Field(
        default=None,
        alias="lastAttemptDate",
        description="Date and time of the last delivery attempt (ISO 8601 format)",
    )
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if delivery failed (optional)",
    )

    @field_validator("subscriber_id")
    @classmethod
    def validate_subscriber_id(cls, v: str) -> str:
        """Validate subscriber ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Subscriber ID is required")
        return v.strip()

    @field_validator("cat_fact_id")
    @classmethod
    def validate_cat_fact_id(cls, v: str) -> str:
        """Validate cat fact ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Cat fact ID is required")
        return v.strip()

    @field_validator("delivery_attempts")
    @classmethod
    def validate_delivery_attempts(cls, v: int) -> int:
        """Validate delivery attempts field"""
        if v < 0:
            raise ValueError("Delivery attempts cannot be negative")
        if v > 10:
            raise ValueError("Delivery attempts cannot exceed 10")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_sent(self) -> None:
        """Mark the email as sent and update timestamps"""
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.sent_date = current_time
        self.last_attempt_date = current_time
        self.delivery_attempts += 1
        self.error_message = None
        self.update_timestamp()

    def mark_failed(self, error_message: str) -> None:
        """Mark the email delivery as failed with error message"""
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.last_attempt_date = current_time
        self.delivery_attempts += 1
        self.error_message = error_message
        self.update_timestamp()

    def reset_for_retry(self) -> None:
        """Reset error message for retry attempt"""
        self.error_message = None
        self.update_timestamp()

    def can_retry(self) -> bool:
        """Check if delivery can be retried (less than 3 attempts and in failed state)"""
        return self.delivery_attempts < 3 and self.state == "failed"

    def is_pending(self) -> bool:
        """Check if delivery is pending"""
        return self.state == "pending"

    def is_sent(self) -> bool:
        """Check if delivery was sent successfully"""
        return self.state == "sent"

    def is_failed(self) -> bool:
        """Check if delivery failed"""
        return self.state == "failed"

    def is_delivered(self) -> bool:
        """Check if delivery was confirmed as delivered"""
        return self.state == "delivered"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["id"] = self.get_id()
        data["state"] = self.state
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
