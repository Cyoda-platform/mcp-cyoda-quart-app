# entity/adoption/version_1/adoption.py

"""
Adoption Entity for Purrfect Pets API

Represents a completed adoption in the system with all required attributes
and state management through Cyoda workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Adoption(CyodaEntity):
    """
    Adoption entity represents a completed adoption in the Purrfect Pets system.

    The Adoption entity uses entity.meta.state to track adoption status:
    - COMPLETED: Adoption has been completed
    - FOLLOW_UP_PENDING: Follow-up is scheduled and pending
    - FOLLOW_UP_COMPLETED: Follow-up has been completed
    - RETURNED: Pet has been returned
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Adoption"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    customer_id: int = Field(
        ..., alias="customerId", description="Customer ID (foreign key)"
    )
    pet_id: int = Field(..., alias="petId", description="Pet ID (foreign key)")
    store_id: int = Field(..., alias="storeId", description="Store ID (foreign key)")
    application_id: int = Field(
        ..., alias="applicationId", description="Application ID (foreign key)"
    )
    adoption_fee: float = Field(
        ..., alias="adoptionFee", description="Adoption fee paid"
    )
    contract_signed: bool = Field(
        ..., alias="contractSigned", description="Whether contract was signed"
    )
    microchip_transferred: bool = Field(
        ...,
        alias="microchipTransferred",
        description="Whether microchip was transferred",
    )
    vaccination_records_provided: bool = Field(
        ...,
        alias="vaccinationRecordsProvided",
        description="Whether vaccination records were provided",
    )

    # Optional fields
    adoption_date: Optional[str] = Field(
        default=None,
        alias="adoptionDate",
        description="Date when adoption was completed (ISO 8601 format)",
    )
    follow_up_date: Optional[str] = Field(
        default=None,
        alias="followUpDate",
        description="Scheduled follow-up date (YYYY-MM-DD)",
    )
    follow_up_completed: bool = Field(
        default=False,
        alias="followUpCompleted",
        description="Whether follow-up has been completed",
    )
    adoption_notes: Optional[str] = Field(
        default=None, alias="adoptionNotes", description="Notes about the adoption"
    )
    return_date: Optional[str] = Field(
        default=None,
        alias="returnDate",
        description="Date when pet was returned (ISO 8601 format)",
    )
    return_reason: Optional[str] = Field(
        default=None, alias="returnReason", description="Reason for returning the pet"
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

    @field_validator("application_id")
    @classmethod
    def validate_application_id(cls, v: int) -> int:
        """Validate application ID"""
        if v <= 0:
            raise ValueError("Application ID must be positive")
        return v

    @field_validator("adoption_fee")
    @classmethod
    def validate_adoption_fee(cls, v: float) -> float:
        """Validate adoption fee"""
        if v < 0:
            raise ValueError("Adoption fee must be non-negative")
        if v > 10000:
            raise ValueError("Adoption fee must be reasonable (max $10,000)")
        return v

    @field_validator("follow_up_date")
    @classmethod
    def validate_follow_up_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate follow-up date"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        # Basic format validation (YYYY-MM-DD)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Follow-up date must be in YYYY-MM-DD format")
        return v.strip()

    @field_validator("adoption_notes")
    @classmethod
    def validate_adoption_notes(cls, v: Optional[str]) -> Optional[str]:
        """Validate adoption notes"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v.strip()) > 2000:
            raise ValueError("Adoption notes must be at most 2000 characters")
        return v.strip()

    @field_validator("return_reason")
    @classmethod
    def validate_return_reason(cls, v: Optional[str]) -> Optional[str]:
        """Validate return reason"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v.strip()) > 1000:
            raise ValueError("Return reason must be at most 1000 characters")
        return v.strip()

    def set_adoption_date(self) -> None:
        """Set adoption date to current timestamp"""
        self.adoption_date = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_return_date(self) -> None:
        """Set return date to current timestamp"""
        self.return_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def complete_follow_up(self) -> None:
        """Mark follow-up as completed"""
        self.follow_up_completed = True
        self.update_timestamp()

    def is_completed(self) -> bool:
        """Check if adoption is completed"""
        return self.state == "completed"

    def is_follow_up_pending(self) -> bool:
        """Check if follow-up is pending"""
        return self.state == "follow_up_pending"

    def is_follow_up_completed(self) -> bool:
        """Check if follow-up is completed"""
        return self.state == "follow_up_completed"

    def is_returned(self) -> bool:
        """Check if pet has been returned"""
        return self.state == "returned"

    def has_follow_up_scheduled(self) -> bool:
        """Check if follow-up is scheduled"""
        return self.follow_up_date is not None

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
