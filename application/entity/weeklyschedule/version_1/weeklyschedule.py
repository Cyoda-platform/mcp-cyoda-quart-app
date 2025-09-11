# entity/weeklyschedule/version_1/weeklyschedule.py

"""
WeeklySchedule Entity for Cyoda Client Application

Represents the weekly schedule for cat fact distribution and manages the weekly cycle.
Tracks the distribution process and statistics for each week.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class WeeklySchedule(CyodaEntity):
    """
    WeeklySchedule represents the weekly schedule for cat fact distribution and manages the weekly cycle.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> created -> fact_assigned -> emails_sent -> completed -> end
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeeklySchedule"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    week_start_date: str = Field(
        ...,
        alias="weekStartDate",
        description="Start date of the week (Monday) in YYYY-MM-DD format",
    )
    week_end_date: str = Field(
        ...,
        alias="weekEndDate",
        description="End date of the week (Sunday) in YYYY-MM-DD format",
    )
    scheduled_send_date: str = Field(
        ...,
        alias="scheduledSendDate",
        description="Planned date for sending cat facts this week in YYYY-MM-DD format",
    )
    cat_fact_id: Optional[str] = Field(
        default=None,
        alias="catFactId",
        description="Foreign key to the CatFact selected for this week (optional)",
    )
    total_subscribers: int = Field(
        default=0,
        alias="totalSubscribers",
        description="Number of active subscribers for this week",
    )
    emails_sent: int = Field(
        default=0,
        alias="emailsSent",
        description="Number of emails successfully sent",
    )
    emails_failed: int = Field(
        default=0,
        alias="emailsFailed",
        description="Number of emails that failed to send",
    )

    @field_validator("week_start_date")
    @classmethod
    def validate_week_start_date(cls, v: str) -> str:
        """Validate week start date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Week start date is required")

        v = v.strip()

        # Basic date format validation (YYYY-MM-DD)
        try:
            date_obj = datetime.strptime(v, "%Y-%m-%d")
            # Check if it's a Monday (weekday() returns 0 for Monday)
            if date_obj.weekday() != 0:
                raise ValueError("Week start date must be a Monday")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Week start date must be in YYYY-MM-DD format")
            raise

        return v

    @field_validator("week_end_date")
    @classmethod
    def validate_week_end_date(cls, v: str) -> str:
        """Validate week end date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Week end date is required")

        v = v.strip()

        # Basic date format validation (YYYY-MM-DD)
        try:
            date_obj = datetime.strptime(v, "%Y-%m-%d")
            # Check if it's a Sunday (weekday() returns 6 for Sunday)
            if date_obj.weekday() != 6:
                raise ValueError("Week end date must be a Sunday")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Week end date must be in YYYY-MM-DD format")
            raise

        return v

    @field_validator("scheduled_send_date")
    @classmethod
    def validate_scheduled_send_date(cls, v: str) -> str:
        """Validate scheduled send date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Scheduled send date is required")

        v = v.strip()

        # Basic date format validation (YYYY-MM-DD)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Scheduled send date must be in YYYY-MM-DD format")

        return v

    @field_validator("total_subscribers", "emails_sent", "emails_failed")
    @classmethod
    def validate_counts(cls, v: int) -> int:
        """Validate count fields"""
        if v < 0:
            raise ValueError("Count values cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_date_consistency(self) -> "WeeklySchedule":
        """Validate date consistency and business logic"""
        try:
            start_date = datetime.strptime(self.week_start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.week_end_date, "%Y-%m-%d")
            send_date = datetime.strptime(self.scheduled_send_date, "%Y-%m-%d")

            # Check if end date is exactly 6 days after start date
            expected_end_date = start_date + timedelta(days=6)
            if end_date != expected_end_date:
                raise ValueError(
                    "Week end date must be exactly 6 days after start date"
                )

            # Check if send date is within the week
            if not (start_date <= send_date <= end_date):
                raise ValueError("Scheduled send date must be within the week")

        except ValueError as e:
            if "time data" in str(e):
                # Date parsing error already handled by field validators
                pass
            else:
                raise

        # Validate email counts consistency
        if self.emails_sent + self.emails_failed > self.total_subscribers:
            raise ValueError(
                "Sum of emails sent and failed cannot exceed total subscribers"
            )

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def assign_cat_fact(self, cat_fact_id: str) -> None:
        """Assign a cat fact to this weekly schedule"""
        self.cat_fact_id = cat_fact_id
        self.update_timestamp()

    def update_email_counts(self, sent: int, failed: int) -> None:
        """Update email sent and failed counts"""
        self.emails_sent = sent
        self.emails_failed = failed
        self.update_timestamp()

    def calculate_success_rate(self) -> float:
        """Calculate email delivery success rate as percentage"""
        if self.total_subscribers == 0:
            return 0.0
        return (self.emails_sent / self.total_subscribers) * 100

    def is_created(self) -> bool:
        """Check if schedule is in created state"""
        return self.state == "created"

    def is_fact_assigned(self) -> bool:
        """Check if cat fact has been assigned"""
        return self.state == "fact_assigned" and self.cat_fact_id is not None

    def is_emails_sent(self) -> bool:
        """Check if emails have been sent"""
        return self.state == "emails_sent"

    def is_completed(self) -> bool:
        """Check if schedule is completed"""
        return self.state == "completed"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["id"] = self.get_id()
        data["state"] = self.state
        data["successRate"] = self.calculate_success_rate()
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
