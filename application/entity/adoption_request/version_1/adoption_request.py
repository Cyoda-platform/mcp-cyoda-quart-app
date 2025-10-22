"""
AdoptionRequest Entity for Cyoda Client Application

Represents an adoption request that flows through a workflow for processing
and approval as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class AdoptionRequest(CyodaEntity):
    """
    AdoptionRequest represents an adoption request that flows through
    a workflow for processing and approval.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> submitted -> reviewed -> approved/rejected -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "AdoptionRequest"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    applicant_name: str = Field(..., description="Name of the adoption applicant")
    applicant_email: str = Field(..., description="Email of the adoption applicant")
    applicant_phone: str = Field(..., description="Phone number of the adoption applicant")
    reason_for_adoption: str = Field(..., description="Reason for adoption request")
    family_size: int = Field(..., ge=1, description="Size of the applicant's family")
    has_other_pets: Optional[bool] = Field(
        default=None,
        alias="hasOtherPets",
        description="Whether the applicant has other pets",
    )
    living_situation: str = Field(..., description="Description of living situation")
    experience_level: str = Field(..., description="Experience level with pets")

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the request was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the request was last updated (ISO 8601 format)",
    )

    # Processing-related fields
    review_notes: Optional[str] = Field(
        default=None,
        alias="reviewNotes",
        description="Notes from the reviewer",
    )
    approval_status: Optional[str] = Field(
        default=None,
        alias="approvalStatus",
        description="Current approval status",
    )
    reviewer_id: Optional[str] = Field(
        default=None,
        alias="reviewerId",
        description="ID of the reviewer",
    )

    # Validation rules
    ALLOWED_EXPERIENCE_LEVELS: ClassVar[List[str]] = [
        "BEGINNER",
        "INTERMEDIATE",
        "ADVANCED",
    ]

    @field_validator("applicant_name")
    @classmethod
    def validate_applicant_name(cls, v: str) -> str:
        """Validate applicant name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Applicant name must be non-empty")
        if len(v) < 2:
            raise ValueError("Applicant name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Applicant name must be at most 100 characters long")
        return v.strip()

    @field_validator("applicant_email")
    @classmethod
    def validate_applicant_email(cls, v: str) -> str:
        """Validate applicant email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Applicant email must be non-empty")
        if "@" not in v:
            raise ValueError("Applicant email must be a valid email address")
        return v.strip()

    @field_validator("applicant_phone")
    @classmethod
    def validate_applicant_phone(cls, v: str) -> str:
        """Validate applicant phone field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Applicant phone must be non-empty")
        return v.strip()

    @field_validator("reason_for_adoption")
    @classmethod
    def validate_reason_for_adoption(cls, v: str) -> str:
        """Validate reason for adoption field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Reason for adoption must be non-empty")
        if len(v) > 500:
            raise ValueError("Reason for adoption must be at most 500 characters long")
        return v.strip()

    @field_validator("living_situation")
    @classmethod
    def validate_living_situation(cls, v: str) -> str:
        """Validate living situation field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Living situation must be non-empty")
        if len(v) > 500:
            raise ValueError("Living situation must be at most 500 characters long")
        return v.strip()

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v: str) -> str:
        """Validate experience level field"""
        if v not in cls.ALLOWED_EXPERIENCE_LEVELS:
            raise ValueError(
                f"Experience level must be one of: {cls.ALLOWED_EXPERIENCE_LEVELS}"
            )
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "AdoptionRequest":
        """Validate business logic rules"""
        if self.family_size < 1:
            raise ValueError("Family size must be at least 1")

        if self.experience_level not in self.ALLOWED_EXPERIENCE_LEVELS:
            raise ValueError(
                f"Experience level must be one of: {self.ALLOWED_EXPERIENCE_LEVELS}"
            )

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_review_notes(self, notes: str) -> None:
        """Set review notes and update timestamp"""
        self.review_notes = notes
        self.update_timestamp()

    def set_approval_status(self, status: str, reviewer_id: str) -> None:
        """Set approval status and reviewer ID"""
        self.approval_status = status
        self.reviewer_id = reviewer_id
        self.update_timestamp()

    def is_ready_for_review(self) -> bool:
        """Check if request is ready for review"""
        return self.state == "submitted"

    def is_approved(self) -> bool:
        """Check if request has been approved"""
        return self.approval_status == "approved"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )

