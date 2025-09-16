"""
AdoptionApplication Entity for Purrfect Pets API

Represents an adoption application submitted by a customer for a specific pet
with all required attributes and workflow state management as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class AdoptionApplication(CyodaEntity):
    """
    AdoptionApplication entity represents an adoption application in the Purrfect Pets system.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> submitted -> under_review -> approved/rejected/withdrawn
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "AdoptionApplication"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    customer_id: int = Field(
        ..., alias="customerId", description="Applicant customer ID"
    )
    pet_id: int = Field(..., alias="petId", description="Pet being applied for")
    application_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="applicationDate",
        description="When application was submitted (ISO 8601 format)",
    )
    reason_for_adoption: str = Field(
        ..., alias="reasonForAdoption", description="Why they want to adopt"
    )
    living_arrangement: str = Field(
        ..., alias="livingArrangement", description="Description of living situation"
    )
    work_schedule: str = Field(
        ..., alias="workSchedule", description="Daily work schedule"
    )
    pet_care_experience: str = Field(
        ..., alias="petCareExperience", description="Previous pet care experience"
    )
    veterinarian_contact: str = Field(
        ..., alias="veterinarianContact", description="Current vet contact info"
    )
    references: str = Field(..., description="Personal references")
    agreed_to_terms: bool = Field(
        ..., alias="agreedToTerms", description="Agreed to adoption terms"
    )
    application_fee: float = Field(
        ..., alias="applicationFee", description="Application fee amount"
    )

    # Optional fields
    notes: Optional[str] = Field(default=None, description="Additional notes")
    reviewer_id: Optional[int] = Field(
        default=None,
        alias="reviewerId",
        description="Staff member reviewing application",
    )
    review_date: Optional[str] = Field(
        default=None,
        alias="reviewDate",
        description="When application was reviewed (ISO 8601 format)",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        alias="rejectionReason",
        description="Reason for rejection if applicable",
    )

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: int) -> int:
        """Validate customer_id field"""
        if v <= 0:
            raise ValueError("Customer ID must be positive")
        return v

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate pet_id field"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("reason_for_adoption")
    @classmethod
    def validate_reason_for_adoption(cls, v: str) -> str:
        """Validate reason_for_adoption field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Reason for adoption must be non-empty")
        if len(v) < 10:
            raise ValueError("Reason for adoption must be at least 10 characters long")
        if len(v) > 500:
            raise ValueError("Reason for adoption must be at most 500 characters long")
        return v.strip()

    @field_validator("living_arrangement")
    @classmethod
    def validate_living_arrangement(cls, v: str) -> str:
        """Validate living_arrangement field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Living arrangement must be non-empty")
        if len(v) < 10:
            raise ValueError("Living arrangement must be at least 10 characters long")
        if len(v) > 500:
            raise ValueError("Living arrangement must be at most 500 characters long")
        return v.strip()

    @field_validator("work_schedule")
    @classmethod
    def validate_work_schedule(cls, v: str) -> str:
        """Validate work_schedule field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Work schedule must be non-empty")
        if len(v) < 5:
            raise ValueError("Work schedule must be at least 5 characters long")
        if len(v) > 200:
            raise ValueError("Work schedule must be at most 200 characters long")
        return v.strip()

    @field_validator("pet_care_experience")
    @classmethod
    def validate_pet_care_experience(cls, v: str) -> str:
        """Validate pet_care_experience field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet care experience must be non-empty")
        if len(v) < 10:
            raise ValueError("Pet care experience must be at least 10 characters long")
        if len(v) > 500:
            raise ValueError("Pet care experience must be at most 500 characters long")
        return v.strip()

    @field_validator("veterinarian_contact")
    @classmethod
    def validate_veterinarian_contact(cls, v: str) -> str:
        """Validate veterinarian_contact field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Veterinarian contact must be non-empty")
        if len(v) < 10:
            raise ValueError("Veterinarian contact must be at least 10 characters long")
        if len(v) > 200:
            raise ValueError("Veterinarian contact must be at most 200 characters long")
        return v.strip()

    @field_validator("references")
    @classmethod
    def validate_references(cls, v: str) -> str:
        """Validate references field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("References must be non-empty")
        if len(v) < 10:
            raise ValueError("References must be at least 10 characters long")
        if len(v) > 500:
            raise ValueError("References must be at most 500 characters long")
        return v.strip()

    @field_validator("agreed_to_terms")
    @classmethod
    def validate_agreed_to_terms(cls, v: bool) -> bool:
        """Validate agreed_to_terms field"""
        if not v:
            raise ValueError("Must agree to terms to submit application")
        return v

    @field_validator("application_fee")
    @classmethod
    def validate_application_fee(cls, v: float) -> float:
        """Validate application_fee field"""
        if v < 0:
            raise ValueError("Application fee must be non-negative")
        if v > 1000:
            raise ValueError("Application fee must be at most $1,000")
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

    @field_validator("reviewer_id")
    @classmethod
    def validate_reviewer_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate reviewer_id field"""
        if v is not None and v <= 0:
            raise ValueError("Reviewer ID must be positive")
        return v

    @field_validator("rejection_reason")
    @classmethod
    def validate_rejection_reason(cls, v: Optional[str]) -> Optional[str]:
        """Validate rejection_reason field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Rejection reason must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    def is_submitted(self) -> bool:
        """Check if application is submitted"""
        return self.state == "submitted"

    def is_under_review(self) -> bool:
        """Check if application is under review"""
        return self.state == "under_review"

    def is_approved(self) -> bool:
        """Check if application is approved"""
        return self.state == "approved"

    def is_rejected(self) -> bool:
        """Check if application is rejected"""
        return self.state == "rejected"

    def is_withdrawn(self) -> bool:
        """Check if application is withdrawn"""
        return self.state == "withdrawn"

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
