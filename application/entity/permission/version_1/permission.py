# entity/permission/version_1/permission.py

"""
Permission Entity for Cyoda Client Application

Represents specific access rights and capabilities within the system
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Permission(CyodaEntity):
    """
    Permission represents specific access rights and capabilities within the system.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Permission"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Permission name (unique)")
    description: str = Field(..., description="Permission description")
    resource: str = Field(..., description="Target resource/module")
    action: str = Field(..., description="Allowed action")
    
    # Optional fields
    is_active: Optional[bool] = Field(
        default=True,
        description="Permission status flag"
    )

    # Timestamps (inherited created_at from CyodaEntity)

    # Valid actions
    VALID_ACTIONS: ClassVar[List[str]] = [
        "create", "read", "update", "delete", "manage", "view", "edit", "admin"
    ]

    # System permissions that cannot be deleted
    SYSTEM_PERMISSIONS: ClassVar[List[str]] = [
        "system.admin", "user.manage", "role.manage", "permission.manage"
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Permission name must be non-empty")
        if len(v) < 3:
            raise ValueError("Permission name must be at least 3 characters long")
        if len(v) > 100:
            raise ValueError("Permission name must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Permission description must be non-empty")
        if len(v) > 500:
            raise ValueError("Permission description must be at most 500 characters long")
        return v.strip()

    @field_validator("resource")
    @classmethod
    def validate_resource(cls, v: str) -> str:
        """Validate resource field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Resource must be non-empty")
        if len(v) > 100:
            raise ValueError("Resource must be at most 100 characters long")
        return v.strip().lower()

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate action field according to business rules"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Action must be non-empty")
        action_lower = v.strip().lower()
        if action_lower not in cls.VALID_ACTIONS:
            raise ValueError(f"Action must be one of: {cls.VALID_ACTIONS}")
        return action_lower

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Permission":
        """Validate business logic rules according to functional requirements"""
        # Ensure resource-action combination makes sense
        if self.resource and self.action:
            # Additional validation for resource-action combinations can be added here
            pass
        return self

    def is_system_permission(self) -> bool:
        """Check if this is a system permission that cannot be deleted"""
        permission_key = f"{self.resource}.{self.action}"
        return permission_key in self.SYSTEM_PERMISSIONS or self.name in self.SYSTEM_PERMISSIONS

    def is_permission_active(self) -> bool:
        """Check if permission is active and can be assigned"""
        return self.is_active is True and self.state == "active"

    def get_permission_key(self) -> str:
        """Get the permission key in format resource.action"""
        return f"{self.resource}.{self.action}"

    def matches_resource_action(self, resource: str, action: str) -> bool:
        """Check if this permission matches the given resource and action"""
        return self.resource == resource.lower() and self.action == action.lower()

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["permission_key"] = self.get_permission_key()
        data["is_system_permission"] = self.is_system_permission()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
