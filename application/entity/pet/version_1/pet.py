# entity/pet/version_1/pet.py

"""
Pet Entity for Purrfect Pets API

Represents a pet in the pet store system with comprehensive information
including species, breed, health status, and adoption workflow management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional
from decimal import Decimal

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity representing animals available for adoption in the pet store.

    Manages pet information, health status, and adoption workflow states:
    initial_state -> available -> reserved -> adopted
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Basic pet information
    name: str = Field(..., description="Pet's name")
    species: str = Field(..., description="Pet species (Dog, Cat, Bird, etc.)")
    breed: str = Field(..., description="Pet breed")
    age_months: int = Field(..., description="Pet age in months", alias="ageMonths")
    color: str = Field(..., description="Pet's primary color")
    size: str = Field(..., description="Pet size category")
    gender: str = Field(..., description="Pet gender")

    # Adoption information
    price: Decimal = Field(..., description="Adoption fee in USD")
    description: str = Field(..., description="Detailed pet description")
    special_needs: Optional[str] = Field(
        default=None, alias="specialNeeds", description="Any special care requirements"
    )

    # Health and status
    health_status: str = Field(
        default="Healthy", alias="healthStatus", description="Current health status"
    )
    vaccination_status: str = Field(
        default="Up to Date",
        alias="vaccinationStatus",
        description="Vaccination status",
    )
    adoption_status: str = Field(
        default="Available",
        alias="adoptionStatus",
        description="Current adoption status",
    )

    # Timestamps
    arrival_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="arrivalDate",
        description="Date when pet arrived at shelter",
    )

    # Processing-related fields (populated during workflow)
    reservation_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="reservationData",
        description="Data populated during reservation processing",
    )
    adoption_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="adoptionData",
        description="Data populated during adoption processing",
    )

    # Validation constants
    ALLOWED_SPECIES: ClassVar[List[str]] = [
        "Dog",
        "Cat",
        "Bird",
        "Fish",
        "Rabbit",
        "Hamster",
        "Guinea Pig",
        "Reptile",
    ]
    ALLOWED_SIZES: ClassVar[List[str]] = ["Small", "Medium", "Large", "Extra Large"]
    ALLOWED_GENDERS: ClassVar[List[str]] = ["Male", "Female", "Unknown"]
    ALLOWED_HEALTH_STATUS: ClassVar[List[str]] = [
        "Healthy",
        "Needs Care",
        "Under Treatment",
        "Recovering",
    ]
    ALLOWED_VACCINATION_STATUS: ClassVar[List[str]] = [
        "Up to Date",
        "Needs Update",
        "Not Vaccinated",
        "Partial",
    ]
    ALLOWED_ADOPTION_STATUS: ClassVar[List[str]] = [
        "Available",
        "Reserved",
        "Adopted",
        "On Hold",
        "Not Available",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Pet name must be at most 50 characters long")
        return v.strip()

    @field_validator("species")
    @classmethod
    def validate_species(cls, v: str) -> str:
        """Validate pet species"""
        if v not in cls.ALLOWED_SPECIES:
            raise ValueError(f"Species must be one of: {cls.ALLOWED_SPECIES}")
        return v

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: str) -> str:
        """Validate pet breed"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Breed must be non-empty")
        if len(v) > 100:
            raise ValueError("Breed must be at most 100 characters long")
        return v.strip()

    @field_validator("age_months")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate pet age"""
        if v < 0:
            raise ValueError("Age cannot be negative")
        if v > 300:  # 25 years max
            raise ValueError("Age cannot exceed 300 months")
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: str) -> str:
        """Validate pet size"""
        if v not in cls.ALLOWED_SIZES:
            raise ValueError(f"Size must be one of: {cls.ALLOWED_SIZES}")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate pet gender"""
        if v not in cls.ALLOWED_GENDERS:
            raise ValueError(f"Gender must be one of: {cls.ALLOWED_GENDERS}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Validate adoption price"""
        if v < 0:
            raise ValueError("Price cannot be negative")
        if v > 10000:
            raise ValueError("Price cannot exceed $10,000")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate pet description"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("health_status")
    @classmethod
    def validate_health_status(cls, v: str) -> str:
        """Validate health status"""
        if v not in cls.ALLOWED_HEALTH_STATUS:
            raise ValueError(
                f"Health status must be one of: {cls.ALLOWED_HEALTH_STATUS}"
            )
        return v

    @field_validator("vaccination_status")
    @classmethod
    def validate_vaccination_status(cls, v: str) -> str:
        """Validate vaccination status"""
        if v not in cls.ALLOWED_VACCINATION_STATUS:
            raise ValueError(
                f"Vaccination status must be one of: {cls.ALLOWED_VACCINATION_STATUS}"
            )
        return v

    @field_validator("adoption_status")
    @classmethod
    def validate_adoption_status(cls, v: str) -> str:
        """Validate adoption status"""
        if v not in cls.ALLOWED_ADOPTION_STATUS:
            raise ValueError(
                f"Adoption status must be one of: {cls.ALLOWED_ADOPTION_STATUS}"
            )
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Pets under treatment should not be available for adoption
        if (
            self.health_status == "Under Treatment"
            and self.adoption_status == "Available"
        ):
            raise ValueError("Pets under treatment cannot be available for adoption")

        # Very young pets (under 8 weeks) should have special handling
        if self.age_months < 2 and not self.special_needs:
            self.special_needs = "Very young - requires special care"

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_reservation_data(self, reservation_data: Dict[str, Any]) -> None:
        """Set reservation data and update timestamp"""
        self.reservation_data = reservation_data
        self.adoption_status = "Reserved"
        self.update_timestamp()

    def set_adoption_data(self, adoption_data: Dict[str, Any]) -> None:
        """Set adoption data and update timestamp"""
        self.adoption_data = adoption_data
        self.adoption_status = "Adopted"
        self.update_timestamp()

    def is_available_for_adoption(self) -> bool:
        """Check if pet is available for adoption"""
        return self.adoption_status == "Available" and self.health_status in [
            "Healthy",
            "Recovering",
        ]

    def is_reserved(self) -> bool:
        """Check if pet is currently reserved"""
        return self.adoption_status == "Reserved"

    def is_adopted(self) -> bool:
        """Check if pet has been adopted"""
        return self.adoption_status == "Adopted"

    def get_age_display(self) -> str:
        """Get human-readable age display"""
        if self.age_months < 12:
            return f"{self.age_months} months"
        years = self.age_months // 12
        months = self.age_months % 12
        if months == 0:
            return f"{years} year{'s' if years != 1 else ''}"
        return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add computed fields
        data["state"] = self.state
        data["ageDisplay"] = self.get_age_display()
        data["availableForAdoption"] = self.is_available_for_adoption()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
