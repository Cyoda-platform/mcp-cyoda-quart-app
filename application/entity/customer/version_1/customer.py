"""
Customer Entity for Purrfect Pets API

Represents a customer who can adopt pets with all required attributes
and workflow state management as specified in functional requirements.
"""

import re
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Customer(CyodaEntity):
    """
    Customer entity represents a customer in the Purrfect Pets system.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> verified -> approved
    or approved -> suspended -> approved or approved -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Customer"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    first_name: str = Field(..., alias="firstName", description="Customer's first name")
    last_name: str = Field(..., alias="lastName", description="Customer's last name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    address: str = Field(..., description="Full address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/province")
    zip_code: str = Field(..., alias="zipCode", description="Postal code")
    date_of_birth: str = Field(..., alias="dateOfBirth", description="Birth date (YYYY-MM-DD)")
    occupation: str = Field(..., description="Job title")
    housing_type: str = Field(..., alias="housingType", description="Type of housing")
    has_yard: bool = Field(..., alias="hasYard", description="Has yard for pets")
    has_other_pets: bool = Field(..., alias="hasOtherPets", description="Owns other pets")
    pet_experience: str = Field(..., alias="petExperience", description="Experience level with pets")
    preferred_contact_method: str = Field(
        ..., 
        alias="preferredContactMethod", 
        description="Preferred contact method"
    )
    registration_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="registrationDate",
        description="When customer registered (ISO 8601 format)"
    )

    # Validation constants
    ALLOWED_HOUSING_TYPES: ClassVar[list[str]] = [
        "House", "Apartment", "Condo", "Townhouse", "Mobile Home", "Other"
    ]
    
    ALLOWED_PET_EXPERIENCE: ClassVar[list[str]] = [
        "Beginner", "Intermediate", "Advanced", "Expert"
    ]
    
    ALLOWED_CONTACT_METHODS: ClassVar[list[str]] = [
        "email", "phone", "text", "mail"
    ]

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate first_name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v) < 2:
            raise ValueError("First name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("First name must be at most 50 characters long")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate last_name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Last name must be non-empty")
        if len(v) < 2:
            raise ValueError("Last name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Last name must be at most 50 characters long")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Email format is invalid")
        
        if len(v) > 100:
            raise ValueError("Email must be at most 100 characters long")
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Phone must be non-empty")
        
        # Remove common phone formatting characters
        cleaned_phone = re.sub(r'[^\d]', '', v)
        if len(cleaned_phone) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        if len(cleaned_phone) > 15:
            raise ValueError("Phone number must have at most 15 digits")
        
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Address must be non-empty")
        if len(v) > 200:
            raise ValueError("Address must be at most 200 characters long")
        return v.strip()

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate city field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("City must be non-empty")
        if len(v) > 50:
            raise ValueError("City must be at most 50 characters long")
        return v.strip()

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate zip_code field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Zip code must be non-empty")
        if len(v) > 20:
            raise ValueError("Zip code must be at most 20 characters long")
        return v.strip()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: str) -> str:
        """Validate date_of_birth field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Date of birth must be non-empty")
        
        # Validate date format (YYYY-MM-DD)
        try:
            birth_date = datetime.strptime(v, "%Y-%m-%d")
            # Check if customer is at least 18 years old
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise ValueError("Customer must be at least 18 years old")
            if age > 120:
                raise ValueError("Invalid birth date")
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Date of birth must be in YYYY-MM-DD format")
            raise e
        
        return v.strip()

    @field_validator("occupation")
    @classmethod
    def validate_occupation(cls, v: str) -> str:
        """Validate occupation field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Occupation must be non-empty")
        if len(v) > 100:
            raise ValueError("Occupation must be at most 100 characters long")
        return v.strip()

    @field_validator("housing_type")
    @classmethod
    def validate_housing_type(cls, v: str) -> str:
        """Validate housing_type field"""
        if v not in cls.ALLOWED_HOUSING_TYPES:
            raise ValueError(f"Housing type must be one of: {cls.ALLOWED_HOUSING_TYPES}")
        return v

    @field_validator("pet_experience")
    @classmethod
    def validate_pet_experience(cls, v: str) -> str:
        """Validate pet_experience field"""
        if v not in cls.ALLOWED_PET_EXPERIENCE:
            raise ValueError(f"Pet experience must be one of: {cls.ALLOWED_PET_EXPERIENCE}")
        return v

    @field_validator("preferred_contact_method")
    @classmethod
    def validate_preferred_contact_method(cls, v: str) -> str:
        """Validate preferred_contact_method field"""
        if v not in cls.ALLOWED_CONTACT_METHODS:
            raise ValueError(f"Preferred contact method must be one of: {cls.ALLOWED_CONTACT_METHODS}")
        return v

    def is_registered(self) -> bool:
        """Check if customer is registered"""
        return self.state == "registered"

    def is_verified(self) -> bool:
        """Check if customer is verified"""
        return self.state == "verified"

    def is_approved(self) -> bool:
        """Check if customer is approved for adoptions"""
        return self.state == "approved"

    def is_suspended(self) -> bool:
        """Check if customer is suspended"""
        return self.state == "suspended"

    def is_inactive(self) -> bool:
        """Check if customer is inactive"""
        return self.state == "inactive"

    def get_full_name(self) -> str:
        """Get customer's full name"""
        return f"{self.first_name} {self.last_name}"

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
