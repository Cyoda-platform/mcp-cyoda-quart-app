# entity/customer/version_1/customer.py

"""
Customer Entity for Purrfect Pets API

Represents a customer in the adoption system with all required attributes
and state management through Cyoda workflow engine.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Customer(CyodaEntity):
    """
    Customer entity represents a customer in the Purrfect Pets system.
    
    The Customer entity uses entity.meta.state to track account status:
    - ACTIVE: Customer account is active
    - SUSPENDED: Customer account is suspended
    - BLACKLISTED: Customer is permanently blacklisted
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Customer"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    first_name: str = Field(..., alias="firstName", description="Customer's first name")
    last_name: str = Field(..., alias="lastName", description="Customer's last name")
    email: str = Field(..., description="Customer's email address (unique)")
    phone: str = Field(..., description="Customer's phone number")
    address: str = Field(..., description="Customer's address")
    city: str = Field(..., description="Customer's city")
    state: str = Field(..., description="Customer's state")
    zip_code: str = Field(..., alias="zipCode", description="Customer's ZIP code")
    date_of_birth: str = Field(..., alias="dateOfBirth", description="Customer's date of birth (YYYY-MM-DD)")
    occupation: str = Field(..., description="Customer's occupation")
    housing_type: str = Field(..., alias="housingType", description="Type of housing (House, Apartment, Condo)")
    has_yard: bool = Field(..., alias="hasYard", description="Whether customer has a yard")
    has_other_pets: bool = Field(..., alias="hasOtherPets", description="Whether customer has other pets")
    
    # Optional fields
    other_pets_description: Optional[str] = Field(
        default=None,
        alias="otherPetsDescription",
        description="Description of other pets"
    )
    previous_pet_experience: Optional[str] = Field(
        default=None,
        alias="previousPetExperience",
        description="Previous pet experience"
    )
    registration_date: Optional[str] = Field(
        default=None,
        alias="registrationDate",
        description="Customer registration date (ISO 8601 format)"
    )

    # Validation rules
    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate first name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("First name must be at most 100 characters")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate last name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Last name must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("Last name must be at most 100 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        if "@" not in v:
            raise ValueError("Email must be a valid email address")
        if len(v.strip()) > 200:
            raise ValueError("Email must be at most 200 characters")
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Phone must be non-empty")
        if len(v.strip()) > 20:
            raise ValueError("Phone must be at most 20 characters")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Address must be non-empty")
        if len(v.strip()) > 500:
            raise ValueError("Address must be at most 500 characters")
        return v.strip()

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate city"""
        if not v or len(v.strip()) == 0:
            raise ValueError("City must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("City must be at most 100 characters")
        return v.strip()

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate state"""
        if not v or len(v.strip()) == 0:
            raise ValueError("State must be non-empty")
        if len(v.strip()) > 50:
            raise ValueError("State must be at most 50 characters")
        return v.strip()

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate ZIP code"""
        if not v or len(v.strip()) == 0:
            raise ValueError("ZIP code must be non-empty")
        if len(v.strip()) > 20:
            raise ValueError("ZIP code must be at most 20 characters")
        return v.strip()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: str) -> str:
        """Validate date of birth"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Date of birth must be non-empty")
        # Basic format validation (YYYY-MM-DD)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date of birth must be in YYYY-MM-DD format")
        return v.strip()

    @field_validator("occupation")
    @classmethod
    def validate_occupation(cls, v: str) -> str:
        """Validate occupation"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Occupation must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("Occupation must be at most 100 characters")
        return v.strip()

    @field_validator("housing_type")
    @classmethod
    def validate_housing_type(cls, v: str) -> str:
        """Validate housing type"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Housing type must be non-empty")
        valid_types = ["House", "Apartment", "Condo", "Townhouse", "Other"]
        if v not in valid_types:
            raise ValueError(f"Housing type must be one of: {valid_types}")
        return v

    def set_registration_date(self) -> None:
        """Set registration date to current timestamp"""
        self.registration_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_active(self) -> bool:
        """Check if customer is active"""
        return self.state == "active"

    def is_suspended(self) -> bool:
        """Check if customer is suspended"""
        return self.state == "suspended"

    def is_blacklisted(self) -> bool:
        """Check if customer is blacklisted"""
        return self.state == "blacklisted"

    def get_full_name(self) -> str:
        """Get customer's full name"""
        return f"{self.first_name} {self.last_name}"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
