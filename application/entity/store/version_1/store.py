# entity/store/version_1/store.py

"""
Store Entity for Purrfect Pets API

Represents a pet store in the system with all required attributes
and state management through Cyoda workflow engine.
"""

from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Store(CyodaEntity):
    """
    Store entity represents a pet store in the Purrfect Pets system.
    
    The Store entity uses entity.meta.state to track operational status:
    - ACTIVE: Store is operational
    - TEMPORARILY_CLOSED: Store is temporarily closed
    - PERMANENTLY_CLOSED: Store is permanently closed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Store"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Store name")
    address: str = Field(..., description="Full address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., alias="zipCode", description="ZIP code")
    phone: str = Field(..., description="Contact phone")
    email: str = Field(..., description="Contact email")
    manager_name: str = Field(..., alias="managerName", description="Store manager's name")
    opening_hours: str = Field(..., alias="openingHours", description="Opening hours (e.g., Mon-Fri 9AM-6PM)")
    capacity: int = Field(..., description="Maximum number of pets")
    current_pet_count: int = Field(
        default=0,
        alias="currentPetCount",
        description="Current number of pets"
    )

    # Validation rules
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate store name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store name must be non-empty")
        if len(v.strip()) > 200:
            raise ValueError("Store name must be at most 200 characters")
        return v.strip()

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store address must be non-empty")
        if len(v.strip()) > 500:
            raise ValueError("Store address must be at most 500 characters")
        return v.strip()

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate city"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store city must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("Store city must be at most 100 characters")
        return v.strip()

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate state"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store state must be non-empty")
        if len(v.strip()) > 50:
            raise ValueError("Store state must be at most 50 characters")
        return v.strip()

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        """Validate ZIP code"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store ZIP code must be non-empty")
        if len(v.strip()) > 20:
            raise ValueError("Store ZIP code must be at most 20 characters")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store phone must be non-empty")
        if len(v.strip()) > 20:
            raise ValueError("Store phone must be at most 20 characters")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email address"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store email must be non-empty")
        if "@" not in v:
            raise ValueError("Store email must be a valid email address")
        if len(v.strip()) > 200:
            raise ValueError("Store email must be at most 200 characters")
        return v.strip().lower()

    @field_validator("manager_name")
    @classmethod
    def validate_manager_name(cls, v: str) -> str:
        """Validate manager name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store manager name must be non-empty")
        if len(v.strip()) > 100:
            raise ValueError("Store manager name must be at most 100 characters")
        return v.strip()

    @field_validator("opening_hours")
    @classmethod
    def validate_opening_hours(cls, v: str) -> str:
        """Validate opening hours"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Store opening hours must be non-empty")
        if len(v.strip()) > 200:
            raise ValueError("Store opening hours must be at most 200 characters")
        return v.strip()

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v: int) -> int:
        """Validate capacity"""
        if v <= 0:
            raise ValueError("Store capacity must be positive")
        if v > 10000:
            raise ValueError("Store capacity must be reasonable (max 10000)")
        return v

    @field_validator("current_pet_count")
    @classmethod
    def validate_current_pet_count(cls, v: int) -> int:
        """Validate current pet count"""
        if v < 0:
            raise ValueError("Current pet count must be non-negative")
        return v

    def is_active(self) -> bool:
        """Check if store is active"""
        return self.state == "active"

    def is_temporarily_closed(self) -> bool:
        """Check if store is temporarily closed"""
        return self.state == "temporarily_closed"

    def is_permanently_closed(self) -> bool:
        """Check if store is permanently closed"""
        return self.state == "permanently_closed"

    def has_capacity(self) -> bool:
        """Check if store has capacity for more pets"""
        return self.current_pet_count < self.capacity

    def increment_pet_count(self) -> None:
        """Increment current pet count"""
        if self.current_pet_count < self.capacity:
            self.current_pet_count += 1
            self.update_timestamp()

    def decrement_pet_count(self) -> None:
        """Decrement current pet count"""
        if self.current_pet_count > 0:
            self.current_pet_count -= 1
            self.update_timestamp()

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
