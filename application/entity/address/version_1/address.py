"""
Address Entity for Purrfect Pets API

Represents address information as specified in functional requirements.
"""

from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Address(CyodaEntity):
    """
    Address entity represents address information.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: ACTIVE, INACTIVE
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Address"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the address")

    # Optional fields
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    zip_code: Optional[str] = Field(
        None, alias="zipCode", description="ZIP or postal code"
    )
    country: Optional[str] = Field(None, description="Country name")

    @field_validator("street")
    @classmethod
    def validate_street(cls, v: Optional[str]) -> Optional[str]:
        """Validate street field"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: Optional[str]) -> Optional[str]:
        """Validate city field"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate zip_code field"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: Optional[str]) -> Optional[str]:
        """Validate country field"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    def is_active(self) -> bool:
        """Check if address is active"""
        return self.state == "active"

    def get_status(self) -> str:
        """Get address status based on state"""
        state_mapping = {"active": "ACTIVE", "inactive": "INACTIVE"}
        return state_mapping.get(self.state, "UNKNOWN")

    def get_formatted_address(self) -> str:
        """Get formatted address string"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
