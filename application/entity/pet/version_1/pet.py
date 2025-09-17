"""
Pet Entity for Purrfect Pets Application

Represents pets available in the Purrfect Pets store for adoption.
Entity state is managed internally via workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents pets available for adoption in the Purrfect Pets store.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> available -> reserved -> adopted
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Pet's name")
    species: str = Field(..., description="Type of animal (e.g., cat, dog, bird)")
    breed: str = Field(..., description="Pet's breed")
    age: int = Field(..., description="Pet's age in years", ge=0, le=30)
    description: str = Field(..., description="Pet's description and personality")
    medical_history: str = Field(..., description="Medical background information")
    adoption_fee: float = Field(..., description="Cost to adopt the pet", ge=0)

    # Relationships - nullable references set during adoption process
    owner_id: Optional[str] = Field(
        default=None, description="Reference to Owner entity (set when adopted)"
    )
    adoption_id: Optional[str] = Field(
        default=None,
        description="Reference to Adoption entity (set during adoption process)",
    )

    # Validation constants
    ALLOWED_SPECIES: ClassVar[list[str]] = [
        "cat",
        "dog",
        "bird",
        "rabbit",
        "hamster",
        "guinea pig",
        "fish",
        "reptile",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v.strip()) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Pet name must be at most 50 characters long")
        return v.strip()

    @field_validator("species")
    @classmethod
    def validate_species(cls, v: str) -> str:
        """Validate species field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Species must be non-empty")
        species_lower = v.strip().lower()
        if species_lower not in cls.ALLOWED_SPECIES:
            raise ValueError(f"Species must be one of: {cls.ALLOWED_SPECIES}")
        return species_lower

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: str) -> str:
        """Validate breed field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Breed must be non-empty")
        if len(v) > 100:
            raise ValueError("Breed must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("medical_history")
    @classmethod
    def validate_medical_history(cls, v: str) -> str:
        """Validate medical history field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Medical history must be non-empty")
        if len(v) > 2000:
            raise ValueError("Medical history must be at most 2000 characters long")
        return v.strip()

    def is_available_for_adoption(self) -> bool:
        """Check if pet is available for adoption"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is reserved"""
        return self.state == "reserved"

    def is_adopted(self) -> bool:
        """Check if pet has been adopted"""
        return self.state == "adopted"

    def set_owner(self, owner_id: str) -> None:
        """Set the owner ID when pet is adopted"""
        self.owner_id = owner_id
        self.update_timestamp()

    def set_adoption(self, adoption_id: str) -> None:
        """Set the adoption ID during adoption process"""
        self.adoption_id = adoption_id
        self.update_timestamp()

    def clear_adoption_references(self) -> None:
        """Clear adoption references when adoption is cancelled"""
        self.adoption_id = None
        self.update_timestamp()

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
