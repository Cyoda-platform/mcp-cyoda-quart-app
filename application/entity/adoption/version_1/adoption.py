"""
Adoption Entity for Purrfect Pets Application

Represents the adoption process linking pets with their new owners.
Entity state is managed internally via workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Adoption(CyodaEntity):
    """
    Adoption entity represents the adoption process linking pets with their new owners.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending -> approved -> completed/cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Adoption"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    application_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="When adoption was requested (ISO date)",
    )
    adoption_date: Optional[str] = Field(
        default=None, description="When adoption was completed (ISO date, nullable)"
    )
    notes: str = Field(..., description="Additional notes about the adoption")
    fee_paid: float = Field(..., description="Amount paid for adoption", ge=0)
    contract_signed: bool = Field(
        default=False, description="Whether adoption contract is signed"
    )

    # Relationships - required references to Pet and Owner
    pet_id: str = Field(..., description="Reference to Pet being adopted")
    owner_id: str = Field(..., description="Reference to adopting Owner")

    @field_validator("application_date")
    @classmethod
    def validate_application_date(cls, v: str) -> str:
        """Validate application date format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Application date must be non-empty")
        # Basic ISO date validation - should be in format YYYY-MM-DDTHH:MM:SSZ
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                "Application date must be in ISO format (YYYY-MM-DDTHH:MM:SSZ)"
            )
        return v.strip()

    @field_validator("adoption_date")
    @classmethod
    def validate_adoption_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate adoption date format"""
        if v is not None:
            if len(v.strip()) == 0:
                return None  # Empty string becomes None
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError(
                    "Adoption date must be in ISO format (YYYY-MM-DDTHH:MM:SSZ)"
                )
            return v.strip()
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str) -> str:
        """Validate notes field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Notes must be non-empty")
        if len(v) > 2000:
            raise ValueError("Notes must be at most 2000 characters long")
        return v.strip()

    @field_validator("pet_id")
    @classmethod
    def validate_pet_id(cls, v: str) -> str:
        """Validate pet ID"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet ID must be non-empty")
        return v.strip()

    @field_validator("owner_id")
    @classmethod
    def validate_owner_id(cls, v: str) -> str:
        """Validate owner ID"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Owner ID must be non-empty")
        return v.strip()

    def is_pending(self) -> bool:
        """Check if adoption is pending"""
        return self.state == "pending"

    def is_approved(self) -> bool:
        """Check if adoption is approved"""
        return self.state == "approved"

    def is_completed(self) -> bool:
        """Check if adoption is completed"""
        return self.state == "completed"

    def is_cancelled(self) -> bool:
        """Check if adoption is cancelled"""
        return self.state == "cancelled"

    def complete_adoption(self) -> None:
        """Mark adoption as completed with current timestamp"""
        self.adoption_date = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def sign_contract(self) -> None:
        """Mark contract as signed"""
        self.contract_signed = True
        self.update_timestamp()

    def set_fee_paid(self, amount: float) -> None:
        """Set the fee paid amount"""
        if amount < 0:
            raise ValueError("Fee paid cannot be negative")
        self.fee_paid = amount
        self.update_timestamp()

    def add_note(self, additional_note: str) -> None:
        """Add additional note to existing notes"""
        if additional_note and len(additional_note.strip()) > 0:
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            self.notes += f"\n[{current_timestamp}] {additional_note.strip()}"
            self.update_timestamp()

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
