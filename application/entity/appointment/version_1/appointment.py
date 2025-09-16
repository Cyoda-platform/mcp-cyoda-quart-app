"""
Appointment Entity for Purrfect Pets API.

Represents a scheduled appointment between a pet, owner, and veterinarian.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import Field, validator

from entity.cyoda_entity import CyodaEntity


class Appointment(CyodaEntity):
    """
    Appointment entity representing a scheduled appointment in the Purrfect Pets system.

    Attributes:
        appointment_id: Unique identifier for the appointment
        pet_id: Reference to the pet
        owner_id: Reference to the owner
        vet_id: Reference to the veterinarian
        appointment_date: Scheduled date and time
        duration_minutes: Expected duration in minutes
        appointment_type: Type of appointment (checkup, vaccination, surgery, etc.)
        reason: Reason for the appointment
        notes: Additional notes
        created_date: When the appointment was created
        estimated_cost: Estimated cost of the appointment
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Appointment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    appointment_id: str = Field(
        ..., description="Unique identifier for the appointment"
    )
    pet_id: str = Field(..., description="Reference to the pet")
    owner_id: str = Field(..., description="Reference to the owner")
    vet_id: str = Field(..., description="Reference to the veterinarian")
    appointment_date: str = Field(..., description="Scheduled date and time")
    duration_minutes: int = Field(
        ..., ge=15, le=480, description="Expected duration in minutes"
    )
    appointment_type: str = Field(..., description="Type of appointment")
    created_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="When the appointment was created",
    )

    # Optional fields
    reason: Optional[str] = Field(None, description="Reason for the appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    estimated_cost: Optional[float] = Field(
        None, ge=0, description="Estimated cost of the appointment"
    )

    @validator("appointment_date")
    def validate_appointment_date(cls, v):
        """Validate appointment date format and ensure it's in the future."""
        if not v or not v.strip():
            raise ValueError("Appointment date cannot be empty")

        try:
            # Parse the ISO format datetime
            appointment_dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            current_dt = datetime.now(timezone.utc)

            # Check if appointment is in the future (allow some buffer for processing)
            if appointment_dt <= current_dt:
                raise ValueError("Appointment date must be in the future")

        except ValueError as e:
            if "Appointment date must be in the future" in str(e):
                raise e
            raise ValueError(
                "Invalid appointment date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
            )

        return v

    @validator("duration_minutes")
    def validate_duration(cls, v):
        """Validate appointment duration."""
        if v < 15:
            raise ValueError("Appointment duration must be at least 15 minutes")
        if v > 480:  # 8 hours
            raise ValueError("Appointment duration cannot exceed 8 hours")
        return v

    @validator("appointment_type")
    def validate_appointment_type(cls, v):
        """Validate appointment type."""
        if not v or not v.strip():
            raise ValueError("Appointment type cannot be empty")

        valid_types = {
            "checkup",
            "vaccination",
            "surgery",
            "dental",
            "grooming",
            "emergency",
            "consultation",
            "follow-up",
            "spay/neuter",
            "x-ray",
            "blood work",
            "medication check",
        }

        if v.lower() not in valid_types:
            # Allow custom types but ensure they're not empty
            pass

        return v.lower()

    @validator("estimated_cost")
    def validate_estimated_cost(cls, v):
        """Validate estimated cost."""
        if v is not None and v < 0:
            raise ValueError("Estimated cost cannot be negative")
        return v

    def is_upcoming(self) -> bool:
        """Check if the appointment is upcoming."""
        try:
            appointment_dt = datetime.fromisoformat(
                self.appointment_date.replace("Z", "+00:00")
            )
            return appointment_dt > datetime.now(timezone.utc)
        except ValueError:
            return False

    def get_duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration_minutes / 60.0

    def __str__(self) -> str:
        """String representation of the appointment."""
        return f"Appointment(appointment_id={self.appointment_id}, pet_id={self.pet_id}, date={self.appointment_date})"
