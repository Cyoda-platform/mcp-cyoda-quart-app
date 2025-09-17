# entity/adoption_application/version_1/adoption_application.py

"""
AdoptionApplication Entity for Purrfect Pets API

Represents an adoption application in the system with all required attributes
and state management through Cyoda workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class AdoptionApplication(CyodaEntity):
    """
    AdoptionApplication entity represents an adoption application in the Purrfect Pets system.
    
    The AdoptionApplication entity uses entity.meta.state to track application progress:
    - SUBMITTED: Application has been submitted
    - UNDER_REVIEW: Application is being reviewed
    - APPROVED: Application has been approved
    - REJECTED: Application has been rejected
    - EXPIRED: Application has expired
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "AdoptionApplication"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    customer_id: int = Field(..., alias="customerId", description="Customer ID (foreign key)")
    pet_id: int = Field(..., alias="petId", description="Pet ID (foreign key)")
    store_id: int = Field(..., alias="storeId", description="Store ID (foreign key)")
    preferred_pickup_date: str = Field(
        ...,
        alias="preferredPickupDate",
        description="Preferred pickup date (YYYY-MM-DD)"
    )
    reason_for_adoption: str = Field(
        ...,
        alias="reasonForAdoption",
        description="Reason for wanting to adopt"
    )
    living_arrangement: str = Field(
        ...,
        alias="livingArrangement",
        description="Description of living arrangement"
    )
    work_schedule: str = Field(
        ...,
        alias="workSchedule",
        description="Work schedule description"
    )
    pet_care_experience: str = Field(
        ...,
        alias="petCareExperience",
        description="Previous pet care experience"
    )
    veterinarian_contact: str = Field(
        ...,
        alias="veterinarianContact",
        description="Veterinarian contact information"
    )
    references: str = Field(..., description="Reference contact information")

    # Optional fields
    application_date: Optional[str] = Field(
        default=None,
        alias="applicationDate",
        description="Application submission date (ISO 8601 format)"
    )
    application_notes: Optional[str] = Field(
        default=None,
        alias="applicationNotes",
        description="Additional application notes"
    )
    review_notes: Optional[str] = Field(
        default=None,
        alias="reviewNotes",
        description="Staff notes during review"
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        alias="rejectionReason",
        description="Reason for rejection if rejected"
    )
    approval_date: Optional[str] = Field(
        default=None,
        alias="approvalDate",
        description="Date when application was approved (ISO 8601 format)"
    )
    rejection_date: Optional[str] = Field(
        default=None,
        alias="rejectionDate",
        description="Date when application was rejected (ISO 8601 format)"
    )

    # Validation rules
    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: int) -> int:
        """Validate customer ID"""
        if v <= 0:
            raise ValueError("Customer ID must be positive")
        return v

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: int) -> int:
        """Validate pet ID"""
        if v <= 0:
            raise ValueError("Pet ID must be positive")
        return v

    @field_validator("store_id")
    @classmethod
    def validate_store_id(cls, v: int) -> int:
        """Validate store ID"""
        if v <= 0:
            raise ValueError("Store ID must be positive")
        return v

    @field_validator("preferred_pickup_date")
    @classmethod
    def validate_preferred_pickup_date(cls, v: str) -> str:
        """Validate preferred pickup date"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Preferred pickup date must be non-empty")
        # Basic format validation (YYYY-MM-DD)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Preferred pickup date must be in YYYY-MM-DD format")
        return v.strip()

    @field_validator("reason_for_adoption")
    @classmethod
    def validate_reason_for_adoption(cls, v: str) -> str:
        """Validate reason for adoption"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Reason for adoption must be non-empty")
        if len(v.strip()) > 1000:
            raise ValueError("Reason for adoption must be at most 1000 characters")
        return v.strip()

    @field_validator("living_arrangement")
    @classmethod
    def validate_living_arrangement(cls, v: str) -> str:
        """Validate living arrangement"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Living arrangement must be non-empty")
        if len(v.strip()) > 1000:
            raise ValueError("Living arrangement must be at most 1000 characters")
        return v.strip()

    @field_validator("work_schedule")
    @classmethod
    def validate_work_schedule(cls, v: str) -> str:
        """Validate work schedule"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Work schedule must be non-empty")
        if len(v.strip()) > 500:
            raise ValueError("Work schedule must be at most 500 characters")
        return v.strip()

    @field_validator("pet_care_experience")
    @classmethod
    def validate_pet_care_experience(cls, v: str) -> str:
        """Validate pet care experience"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet care experience must be non-empty")
        if len(v.strip()) > 1000:
            raise ValueError("Pet care experience must be at most 1000 characters")
        return v.strip()

    @field_validator("veterinarian_contact")
    @classmethod
    def validate_veterinarian_contact(cls, v: str) -> str:
        """Validate veterinarian contact"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Veterinarian contact must be non-empty")
        if len(v.strip()) > 500:
            raise ValueError("Veterinarian contact must be at most 500 characters")
        return v.strip()

    @field_validator("references")
    @classmethod
    def validate_references(cls, v: str) -> str:
        """Validate references"""
        if not v or len(v.strip()) == 0:
            raise ValueError("References must be non-empty")
        if len(v.strip()) > 1000:
            raise ValueError("References must be at most 1000 characters")
        return v.strip()

    def set_application_date(self) -> None:
        """Set application date to current timestamp"""
        self.application_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_approval_date(self) -> None:
        """Set approval date to current timestamp"""
        self.approval_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_rejection_date(self) -> None:
        """Set rejection date to current timestamp"""
        self.rejection_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

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

    def is_expired(self) -> bool:
        """Check if application is expired"""
        return self.state == "expired"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
