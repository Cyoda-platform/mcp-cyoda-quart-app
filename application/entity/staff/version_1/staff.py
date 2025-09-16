"""
Staff Entity for Purrfect Pets API

Represents a staff member working at the pet store with all required attributes
and workflow state management as specified in functional requirements.
"""

import re
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Staff(CyodaEntity):
    """
    Staff entity represents a staff member in the Purrfect Pets system.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> on_leave/suspended/terminated
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Staff"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    first_name: str = Field(
        ..., alias="firstName", description="Staff member's first name"
    )
    last_name: str = Field(
        ..., alias="lastName", description="Staff member's last name"
    )
    email: str = Field(..., description="Work email address")
    phone: str = Field(..., description="Work phone number")
    role: str = Field(..., description="Job role")
    department: str = Field(..., description="Department name")
    hire_date: str = Field(
        ..., alias="hireDate", description="Date of hire (YYYY-MM-DD)"
    )
    salary: float = Field(..., description="Annual salary")
    is_active: bool = Field(..., alias="isActive", description="Employment status")

    # Optional fields
    certifications: Optional[str] = Field(
        default=None, description="Relevant certifications"
    )
    specializations: Optional[str] = Field(
        default=None, description="Areas of expertise"
    )

    # Validation constants
    ALLOWED_ROLES: ClassVar[list[str]] = [
        "Manager",
        "Veterinarian",
        "Caretaker",
        "Adoption Counselor",
        "Receptionist",
        "Groomer",
        "Trainer",
        "Volunteer Coordinator",
    ]

    ALLOWED_DEPARTMENTS: ClassVar[list[str]] = [
        "Medical",
        "Adoption",
        "Administration",
        "Grooming",
        "Training",
        "Volunteer",
        "Maintenance",
        "Customer Service",
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
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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
        cleaned_phone = re.sub(r"[^\d]", "", v)
        if len(cleaned_phone) < 10:
            raise ValueError("Phone number must have at least 10 digits")
        if len(cleaned_phone) > 15:
            raise ValueError("Phone number must have at most 15 digits")

        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role field"""
        if v not in cls.ALLOWED_ROLES:
            raise ValueError(f"Role must be one of: {cls.ALLOWED_ROLES}")
        return v

    @field_validator("department")
    @classmethod
    def validate_department(cls, v: str) -> str:
        """Validate department field"""
        if v not in cls.ALLOWED_DEPARTMENTS:
            raise ValueError(f"Department must be one of: {cls.ALLOWED_DEPARTMENTS}")
        return v

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: str) -> str:
        """Validate hire_date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Hire date must be non-empty")

        # Validate date format (YYYY-MM-DD)
        try:
            hire_date = datetime.strptime(v, "%Y-%m-%d")
            # Check if hire date is not in the future
            today = datetime.now()
            if hire_date.date() > today.date():
                raise ValueError("Hire date cannot be in the future")
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Hire date must be in YYYY-MM-DD format")
            raise e

        return v.strip()

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: float) -> float:
        """Validate salary field"""
        if v < 0:
            raise ValueError("Salary must be non-negative")
        if v > 1000000:
            raise ValueError("Salary must be at most $1,000,000")
        return v

    @field_validator("certifications")
    @classmethod
    def validate_certifications(cls, v: Optional[str]) -> Optional[str]:
        """Validate certifications field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Certifications must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    @field_validator("specializations")
    @classmethod
    def validate_specializations(cls, v: Optional[str]) -> Optional[str]:
        """Validate specializations field"""
        if v is not None:
            if len(v) > 500:
                raise ValueError("Specializations must be at most 500 characters long")
            return v.strip() if v.strip() else None
        return v

    def is_staff_active(self) -> bool:
        """Check if staff member is active (workflow state)"""
        return self.state == "active"

    def is_on_leave(self) -> bool:
        """Check if staff member is on leave"""
        return self.state == "on_leave"

    def is_suspended(self) -> bool:
        """Check if staff member is suspended"""
        return self.state == "suspended"

    def is_terminated(self) -> bool:
        """Check if staff member is terminated"""
        return self.state == "terminated"

    def get_full_name(self) -> str:
        """Get staff member's full name"""
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
