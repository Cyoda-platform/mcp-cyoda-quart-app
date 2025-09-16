"""
EmailDelivery entity for the cat fact subscription system.
"""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from entity.cyoda_entity import CyodaEntity


class EmailDelivery(CyodaEntity):
    """
    Represents the delivery of a cat fact email to a specific subscriber.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailDelivery"
    ENTITY_VERSION: ClassVar[int] = 1

    # Business fields
    id: Optional[int] = Field(
        default=None, description="Unique identifier for the email delivery"
    )
    subscriberId: int = Field(..., description="Foreign key to Subscriber entity")
    catFactId: int = Field(..., description="Foreign key to CatFact entity")
    sentDate: Optional[datetime] = Field(
        default=None, description="Date and time when the email was sent"
    )
    deliveryAttempts: int = Field(
        default=0, description="Number of delivery attempts made"
    )
    lastAttemptDate: Optional[datetime] = Field(
        default=None, description="Date and time of the last delivery attempt"
    )
    errorMessage: Optional[str] = Field(
        default=None, description="Error message if delivery failed"
    )
    opened: bool = Field(
        default=False, description="Whether the email was opened by the recipient"
    )
    openedDate: Optional[datetime] = Field(
        default=None, description="Date and time when the email was opened"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    def __str__(self) -> str:
        """String representation of the email delivery."""
        return f"EmailDelivery(id={self.id}, subscriberId={self.subscriberId}, catFactId={self.catFactId}, state={self.state})"
