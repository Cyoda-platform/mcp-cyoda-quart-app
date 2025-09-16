"""
WeeklySchedule entity for the cat fact subscription system.
"""

from datetime import date, datetime
from typing import ClassVar, Optional

from pydantic import Field

from entity.cyoda_entity import CyodaEntity


class WeeklySchedule(CyodaEntity):
    """
    Represents the weekly schedule for cat fact distribution.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeeklySchedule"
    ENTITY_VERSION: ClassVar[int] = 1

    # Business fields
    id: Optional[int] = Field(
        default=None, description="Unique identifier for the schedule"
    )
    weekStartDate: date = Field(..., description="Start date of the week")
    weekEndDate: date = Field(..., description="End date of the week")
    catFactId: Optional[int] = Field(
        default=None, description="Foreign key to the CatFact for this week"
    )
    scheduledDate: datetime = Field(
        ..., description="When the cat fact retrieval and sending is scheduled"
    )
    executedDate: Optional[datetime] = Field(
        default=None, description="When the schedule was actually executed"
    )
    subscriberCount: int = Field(
        default=0, description="Number of active subscribers at the time of execution"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }

    def __str__(self) -> str:
        """String representation of the weekly schedule."""
        return f"WeeklySchedule(id={self.id}, weekStartDate={self.weekStartDate}, state={self.state})"
