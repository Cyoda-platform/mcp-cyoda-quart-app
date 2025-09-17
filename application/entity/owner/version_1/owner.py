"""
Owner Entity for Purrfect Pets Application

Represents individuals who can adopt pets from the Purrfect Pets store.
Entity state is managed internally via workflow engine.
"""

from typing import ClassVar, Optional

from pydantic import ConfigDict, EmailStr, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Owner(CyodaEntity):
    """
    Owner entity represents individuals who can adopt pets from the Purrfect Pets store.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> verified -> active
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Owner"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Owner's full name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: str = Field(..., description="Phone number")
    address: str = Field(..., description="Home address")
    experience: str = Field(..., description="Pet ownership experience level")
    preferences: str = Field(..., description="Preferred pet types and characteristics")
    verification_documents: Optional[str] = Field(
        default=None, description="Uploaded verification files"
    )

    # Relationships - lists of references to adopted pets and adoptions
    pet_ids: list[str] = Field(
        default_factory=list, description="List of adopted pet references"
    )
    adoption_ids: list[str] = Field(
        default_factory=list, description="List of adoption process references"
    )

    # Validation constants
    ALLOWED_EXPERIENCE_LEVELS: ClassVar[list[str]] = [
        "beginner",
        "intermediate",
        "experienced",
        "expert",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate owner name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Owner name must be non-empty")
        if len(v.strip()) < 2:
            raise ValueError("Owner name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Owner name must be at most 100 characters long")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Phone number must be non-empty")
        # Basic phone validation - remove spaces and check length
        phone_clean = (
            v.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        if len(phone_clean) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        if len(phone_clean) > 15:
            raise ValueError("Phone number must be at most 15 digits")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Address must be non-empty")
        if len(v) > 500:
            raise ValueError("Address must be at most 500 characters long")
        return v.strip()

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v: str) -> str:
        """Validate experience level"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Experience level must be non-empty")
        experience_lower = v.strip().lower()
        if experience_lower not in cls.ALLOWED_EXPERIENCE_LEVELS:
            raise ValueError(
                f"Experience must be one of: {cls.ALLOWED_EXPERIENCE_LEVELS}"
            )
        return experience_lower

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v: str) -> str:
        """Validate preferences"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Preferences must be non-empty")
        if len(v) > 1000:
            raise ValueError("Preferences must be at most 1000 characters long")
        return v.strip()

    @field_validator("verification_documents")
    @classmethod
    def validate_verification_documents(cls, v: Optional[str]) -> Optional[str]:
        """Validate verification documents"""
        if v is not None:
            if len(v.strip()) == 0:
                return None  # Empty string becomes None
            if len(v) > 500:
                raise ValueError(
                    "Verification documents path must be at most 500 characters long"
                )
            return v.strip()
        return v

    def is_registered(self) -> bool:
        """Check if owner is registered"""
        return self.state == "registered"

    def is_verified(self) -> bool:
        """Check if owner is verified"""
        return self.state == "verified"

    def is_active(self) -> bool:
        """Check if owner is active"""
        return self.state == "active"

    def can_adopt_pets(self) -> bool:
        """Check if owner can adopt pets (verified or active)"""
        return self.state in ["verified", "active"]

    def has_verification_documents(self) -> bool:
        """Check if owner has provided verification documents"""
        return (
            self.verification_documents is not None
            and len(self.verification_documents.strip()) > 0
        )

    def add_pet(self, pet_id: str) -> None:
        """Add a pet to the owner's list of adopted pets"""
        if pet_id not in self.pet_ids:
            self.pet_ids.append(pet_id)
            self.update_timestamp()

    def add_adoption(self, adoption_id: str) -> None:
        """Add an adoption to the owner's list of adoptions"""
        if adoption_id not in self.adoption_ids:
            self.adoption_ids.append(adoption_id)
            self.update_timestamp()

    def remove_adoption(self, adoption_id: str) -> None:
        """Remove an adoption from the owner's list (when cancelled)"""
        if adoption_id in self.adoption_ids:
            self.adoption_ids.remove(adoption_id)
            self.update_timestamp()

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
