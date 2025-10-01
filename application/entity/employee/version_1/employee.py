# entity/employee/version_1/employee.py

"""
Employee Entity for Cyoda Client Application

Represents staff members with personal and professional information
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Employee(CyodaEntity):
    """
    Employee represents staff members with personal and professional information.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> onboarding -> active -> on_leave/terminated
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Employee"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    employee_id: str = Field(..., description="Unique employee identifier")
    first_name: str = Field(..., description="Employee's first name")
    last_name: str = Field(..., description="Employee's last name")
    email: str = Field(..., description="Employee email address (unique)")
    hire_date: str = Field(..., description="Employment start date (ISO 8601 format)")
    position_id: str = Field(..., description="Assigned position ID")

    # Optional fields
    phone: Optional[str] = Field(default=None, description="Phone number")
    user_id: Optional[str] = Field(
        default=None, description="Associated user account ID"
    )
    department: Optional[str] = Field(default=None, description="Department name")
    is_active: Optional[bool] = Field(
        default=True, description="Employment status flag"
    )

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        """Validate employee ID field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Employee ID must be non-empty")
        if len(v) < 3:
            raise ValueError("Employee ID must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Employee ID must be at most 50 characters long")
        return v.strip().upper()

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """Validate first name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("First name must be non-empty")
        if len(v) > 100:
            raise ValueError("First name must be at most 100 characters long")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        """Validate last name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Last name must be non-empty")
        if len(v) > 100:
            raise ValueError("Last name must be at most 100 characters long")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")
        if "@" not in v or "." not in v:
            raise ValueError("Email must be a valid email address")
        if len(v) > 255:
            raise ValueError("Email must be at most 255 characters long")
        return v.strip().lower()

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: str) -> str:
        """Validate hire date field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Hire date must be non-empty")
        try:
            # Validate ISO 8601 format
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Hire date must be in ISO 8601 format")
        return v.strip()

    @field_validator("position_id")
    @classmethod
    def validate_position_id(cls, v: str) -> str:
        """Validate position ID field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Position ID must be non-empty")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone field"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v) > 20:
            raise ValueError("Phone number must be at most 20 characters long")
        return v.strip()

    @field_validator("department")
    @classmethod
    def validate_department(cls, v: Optional[str]) -> Optional[str]:
        """Validate department field"""
        if v is None:
            return v
        if len(v.strip()) == 0:
            return None
        if len(v) > 100:
            raise ValueError("Department must be at most 100 characters long")
        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Employee":
        """Validate business logic rules according to functional requirements"""
        # Additional business logic validation can be added here
        return self

    def get_full_name(self) -> str:
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}"

    def is_employee_active(self) -> bool:
        """Check if employee is active"""
        return self.is_active is True and self.state == "active"

    def has_user_account(self) -> bool:
        """Check if employee has an associated user account"""
        return self.user_id is not None and len(self.user_id.strip()) > 0

    def is_on_leave(self) -> bool:
        """Check if employee is on leave"""
        return self.state == "on_leave"

    def is_terminated(self) -> bool:
        """Check if employee is terminated"""
        return self.state == "terminated"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["full_name"] = self.get_full_name()
        data["has_user_account"] = self.has_user_account()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
