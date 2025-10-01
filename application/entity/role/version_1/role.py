# entity/role/version_1/role.py

"""
Role Entity for Cyoda Client Application

Represents user roles that group permissions for access control
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Role(CyodaEntity):
    """
    Role represents user roles that group permissions for access control.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> draft -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Role"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Role name (unique)")
    description: str = Field(..., description="Role description")

    # Optional fields
    permission_ids: Optional[List[str]] = Field(
        default_factory=list, description="Array of assigned permission IDs"
    )
    is_active: Optional[bool] = Field(default=True, description="Role status flag")

    # Timestamps (inherited created_at from CyodaEntity)
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the entity was last updated (ISO 8601 format)",
    )

    # System role protection
    SYSTEM_ROLES: ClassVar[List[str]] = ["admin", "system", "super_admin"]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Role name must be non-empty")
        if len(v) < 2:
            raise ValueError("Role name must be at least 2 characters long")
        if len(v) > 100:
            raise ValueError("Role name must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Role description must be non-empty")
        if len(v) > 500:
            raise ValueError("Role description must be at most 500 characters long")
        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Role":
        """Validate business logic rules according to functional requirements"""
        # Additional business logic validation can be added here
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add_permission(self, permission_id: str) -> None:
        """Add a permission to the role"""
        if self.permission_ids is None:
            self.permission_ids = []
        if permission_id not in self.permission_ids:
            self.permission_ids.append(permission_id)
            self.update_timestamp()

    def remove_permission(self, permission_id: str) -> None:
        """Remove a permission from the role"""
        if self.permission_ids and permission_id in self.permission_ids:
            self.permission_ids.remove(permission_id)
            self.update_timestamp()

    def has_permission(self, permission_id: str) -> bool:
        """Check if role has a specific permission"""
        return self.permission_ids is not None and permission_id in self.permission_ids

    def is_system_role(self) -> bool:
        """Check if this is a system role that cannot be deleted"""
        return self.name.lower() in self.SYSTEM_ROLES

    def is_role_active(self) -> bool:
        """Check if role is active and can be assigned"""
        return self.is_active is True and self.state == "active"

    def get_permission_count(self) -> int:
        """Get the number of permissions assigned to this role"""
        return len(self.permission_ids) if self.permission_ids else 0

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["permission_count"] = self.get_permission_count()
        data["is_system_role"] = self.is_system_role()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
