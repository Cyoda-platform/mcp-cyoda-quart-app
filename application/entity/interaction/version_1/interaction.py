# entity/interaction/version_1/interaction.py

"""
Interaction Entity for Cyoda Client Application

Represents user interactions with cat facts (opens, clicks, unsubscribes, etc.).
Manages interaction tracking and analytics data.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Interaction(CyodaEntity):
    """
    Interaction represents user interactions with cat fact emails.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> recorded -> processed -> end
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Interaction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Valid interaction types
    VALID_INTERACTION_TYPES: ClassVar[List[str]] = [
        "EMAIL_OPEN",
        "LINK_CLICK",
        "UNSUBSCRIBE",
        "BOUNCE",
        "COMPLAINT",
    ]

    # Required fields from functional requirements
    subscriber_id: str = Field(
        ..., alias="subscriberId", description="Foreign key to Subscriber entity"
    )
    email_delivery_id: Optional[str] = Field(
        default=None,
        alias="emailDeliveryId",
        description="Foreign key to EmailDelivery entity (optional)",
    )
    interaction_type: str = Field(
        ...,
        alias="interactionType",
        description="Type of interaction (EMAIL_OPEN, LINK_CLICK, UNSUBSCRIBE, etc.)",
    )
    interaction_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="interactionDate",
        description="Date and time when the interaction occurred (ISO 8601 format)",
    )
    ip_address: Optional[str] = Field(
        default=None,
        alias="ipAddress",
        description="IP address of the user (optional, for analytics)",
    )
    user_agent: Optional[str] = Field(
        default=None,
        alias="userAgent",
        description="User agent string (optional, for analytics)",
    )
    additional_data: Optional[str] = Field(
        default=None,
        alias="additionalData",
        description="Additional interaction data in JSON format (optional)",
    )

    @field_validator("subscriber_id")
    @classmethod
    def validate_subscriber_id(cls, v: str) -> str:
        """Validate subscriber ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Subscriber ID is required")
        return v.strip()

    @field_validator("interaction_type")
    @classmethod
    def validate_interaction_type(cls, v: str) -> str:
        """Validate interaction type field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Interaction type is required")

        v = v.strip().upper()
        if v not in cls.VALID_INTERACTION_TYPES:
            raise ValueError(
                f"Invalid interaction type. Must be one of: {cls.VALID_INTERACTION_TYPES}"
            )

        return v

    @field_validator("email_delivery_id")
    @classmethod
    def validate_email_delivery_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate email delivery ID field"""
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        return v

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address field"""
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        # Basic IP address format validation (IPv4 or IPv6)
        if not (("." in v and len(v.split(".")) == 4) or (":" in v)):
            raise ValueError("Invalid IP address format")

        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_unsubscribe_interaction(self) -> bool:
        """Check if this is an unsubscribe interaction"""
        return self.interaction_type == "UNSUBSCRIBE"

    def is_email_open(self) -> bool:
        """Check if this is an email open interaction"""
        return self.interaction_type == "EMAIL_OPEN"

    def is_link_click(self) -> bool:
        """Check if this is a link click interaction"""
        return self.interaction_type == "LINK_CLICK"

    def is_bounce(self) -> bool:
        """Check if this is a bounce interaction"""
        return self.interaction_type == "BOUNCE"

    def is_complaint(self) -> bool:
        """Check if this is a complaint interaction"""
        return self.interaction_type == "COMPLAINT"

    def is_recorded(self) -> bool:
        """Check if interaction has been recorded"""
        return self.state == "recorded"

    def is_processed(self) -> bool:
        """Check if interaction has been processed"""
        return self.state == "processed"

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
