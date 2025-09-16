"""
Subscriber entity for the cat fact subscription system.
"""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import EmailStr, Field

from entity.cyoda_entity import CyodaEntity


class Subscriber(CyodaEntity):
    """
    Represents a user who has subscribed to receive weekly cat facts via email.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Subscriber"
    ENTITY_VERSION: ClassVar[int] = 1

    # Business fields
    id: Optional[int] = Field(
        default=None, description="Unique identifier for the subscriber"
    )
    email: EmailStr = Field(
        ..., description="Email address of the subscriber (unique, required)"
    )
    firstName: Optional[str] = Field(
        default=None, description="First name of the subscriber"
    )
    lastName: Optional[str] = Field(
        default=None, description="Last name of the subscriber"
    )
    subscriptionDate: Optional[datetime] = Field(
        default=None, description="Date and time when the user subscribed"
    )
    isActive: bool = Field(
        default=False, description="Whether the subscription is currently active"
    )
    unsubscribeToken: Optional[str] = Field(
        default=None, description="Unique token for unsubscribing (UUID)"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    def __str__(self) -> str:
        """String representation of the subscriber."""
        return f"Subscriber(id={self.id}, email={self.email}, isActive={self.isActive})"
