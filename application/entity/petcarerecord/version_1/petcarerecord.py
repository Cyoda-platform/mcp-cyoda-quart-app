"""
PetCareRecord Entity for Purrfect Pets API

Represents a pet care record tracking medical care, grooming, and other services
provided to pets with all required attributes and workflow state management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class PetCareRecord(CyodaEntity):
    """
    PetCareRecord entity represents a care record for a pet in the Purrfect Pets system.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> scheduled -> completed/cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "PetCareRecord"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    pet_id: int = Field(..., alias="petId", description="Pet this record belongs to")
    care_date: str = Field(
        ..., alias="careDate", description="Date of care (ISO 8601 format)"
    )
    care_type: str = Field(
        ...,
        alias="careType",
        description="Type of care (e.g., Vaccination, Checkup, Treatment, Grooming)",
    )
    description: str = Field(..., description="Detailed description of care")
    veterinarian: str = Field(..., description="Vet or staff member name")
    cost: float = Field(..., description="Cost of care")

    # Optional fields
    next_due_date: Optional[str] = Field(
        default=None,
        alias="nextDueDate",
        description="When next care is due (YYYY-MM-DD format)",
    )
    medications: Optional[str] = Field(
        default=None, description="Any medications given"
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")
    attachments: Optional[str] = Field(
        default=None, description="URLs to documents/photos"
    )

    # Validation constants
    ALLOWED_CARE_TYPES: ClassVar[list[str]] = [
        "Vaccination",
        "Checkup",
        "Treatment",
        "Grooming",
        "Surgery",
        "Dental",
        "Emergency",
        "Spay/Neuter",
        "Microchip",
        "Other",
    ]

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate pet_id field"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("care_date")
    @classmethod
    def validate_care_date(cls, v: str) -> str:
        """Validate care_date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Care date must be non-empty")

        # Validate ISO 8601 datetime format
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Care date must be in ISO 8601 format")

        return v.strip()

    @field_validator("care_type")
    @classmethod
    def validate_care_type(cls, v: str) -> str:
        """Validate care_type field"""
        if v not in cls.ALLOWED_CARE_TYPES:
            raise ValueError(f"Care type must be one of: {cls.ALLOWED_CARE_TYPES}")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) < 5:
            raise ValueError("Description must be at least 5 characters long")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("veterinarian")
    @classmethod
    def validate_veterinarian(cls, v: str) -> str:
        """Validate veterinarian field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Veterinarian must be non-empty")
        if len(v) < 2:
            raise ValueError("Veterinarian name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Veterinarian name must be at most 100 characters long")
        return v.strip()

    @field_validator("cost")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        """Validate cost field"""
        if v < 0:
            raise ValueError("Cost must be non-negative")
        if v > 10000:
            raise ValueError("Cost must be at most $10,000")
        return v

    @field_validator("next_due_date")
    @classmethod
    def validate_next_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate next_due_date field"""
        if v is not None:
            if not v.strip():
                return None

            # Validate date format (YYYY-MM-DD)
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Next due date must be in YYYY-MM-DD format")

            return v.strip()
        return v

    @field_validator("medications")
    @classmethod
    def validate_medications(cls, v: Optional[str]) -> Optional[str]:
        """Validate medications field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Medications must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes field"""
        if v is not None:
            if len(v) > 1000:
                raise ValueError("Notes must be at most 1000 characters long")
            return v.strip() if v.strip() else None
        return v

    @field_validator("attachments")
    @classmethod
    def validate_attachments(cls, v: Optional[str]) -> Optional[str]:
        """Validate attachments field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Attachments must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    def is_scheduled(self) -> bool:
        """Check if care is scheduled"""
        return self.state == "scheduled"

    def is_completed(self) -> bool:
        """Check if care is completed"""
        return self.state == "completed"

    def is_cancelled(self) -> bool:
        """Check if care is cancelled"""
        return self.state == "cancelled"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
