"""
Response Models for Application API endpoints.

Provides comprehensive response schemas for all API operations with proper
validation and documentation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Common Response Models
class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    code: Optional[str] = Field(default=None, description="Error code")
    timestamp: Optional[str] = Field(default=None, description="Error timestamp")


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error: str = Field(..., description="Validation error message")
    field_errors: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Field-specific validation errors"
    )
    code: str = Field(default="VALIDATION_ERROR", description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class DeleteResponse(BaseModel):
    """Response model for entity deletion operations"""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Deletion result message")
    entity_id: str = Field(..., description="ID of the deleted entity")


class ExistsResponse(BaseModel):
    """Response model for entity existence check"""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(..., description="ID of the checked entity")


class CountResponse(BaseModel):
    """Response model for entity count operations"""

    count: int = Field(..., description="Total number of entities")


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., description="ID of the entity")
    available_transitions: List[str] = Field(
        ..., description="List of available transition names"
    )
    current_state: Optional[str] = Field(None, description="Current entity state")


class TransitionResponse(BaseModel):
    """Response model for transition execution"""

    entity_id: str = Field(..., description="ID of the entity")
    transition_name: str = Field(..., description="Name of executed transition")
    previous_state: Optional[str] = Field(None, description="Previous entity state")
    new_state: str = Field(..., description="New entity state")
    success: bool = Field(..., description="Transition success status")
    message: Optional[str] = Field(
        default=None, description="Transition result message"
    )
    timestamp: Optional[str] = Field(default=None, description="Transition timestamp")


# User Response Models
class UserResponse(BaseModel):
    """Response model for User operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    is_active: bool = Field(..., description="Active status")
    role_ids: List[str] = Field(..., description="Assigned role IDs")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Last update timestamp"
    )
    last_login: Optional[str] = Field(
        default=None, description="Last login timestamp"
    )


class UserListResponse(BaseModel):
    """Response model for User list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of User objects"
    )
    total: int = Field(..., description="Total number of entities")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class UserSearchResponse(BaseModel):
    """Response model for User search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied search query"
    )


# Role Response Models
class RoleResponse(BaseModel):
    """Response model for Role operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    permission_ids: List[str] = Field(..., description="Assigned permission IDs")
    is_active: bool = Field(..., description="Active status")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Last update timestamp"
    )


class RoleListResponse(BaseModel):
    """Response model for Role list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of Role objects"
    )
    total: int = Field(..., description="Total number of entities")


class RoleSearchResponse(BaseModel):
    """Response model for Role search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")


# Permission Response Models
class PermissionResponse(BaseModel):
    """Response model for Permission operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    name: str = Field(..., description="Permission name")
    description: str = Field(..., description="Permission description")
    resource: str = Field(..., description="Target resource")
    action: str = Field(..., description="Allowed action")
    is_active: bool = Field(..., description="Active status")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp"
    )


class PermissionListResponse(BaseModel):
    """Response model for Permission list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of Permission objects"
    )
    total: int = Field(..., description="Total number of entities")


class PermissionSearchResponse(BaseModel):
    """Response model for Permission search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")


# Employee Response Models
class EmployeeResponse(BaseModel):
    """Response model for Employee operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    employee_id: str = Field(..., description="Employee ID")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    hire_date: str = Field(..., description="Hire date")
    position_id: str = Field(..., description="Position ID")
    user_id: Optional[str] = Field(default=None, description="User account ID")
    department: Optional[str] = Field(default=None, description="Department")
    is_active: bool = Field(..., description="Active status")
    state: str = Field(..., description="Current workflow state")


class EmployeeListResponse(BaseModel):
    """Response model for Employee list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of Employee objects"
    )
    total: int = Field(..., description="Total number of entities")


class EmployeeSearchResponse(BaseModel):
    """Response model for Employee search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")


# Position Response Models
class PositionResponse(BaseModel):
    """Response model for Position operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    title: str = Field(..., description="Position title")
    description: str = Field(..., description="Position description")
    department: str = Field(..., description="Department")
    level: Optional[str] = Field(default=None, description="Position level")
    salary_range_min: Optional[float] = Field(default=None, description="Minimum salary")
    salary_range_max: Optional[float] = Field(default=None, description="Maximum salary")
    is_active: bool = Field(..., description="Active status")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Last update timestamp"
    )


class PositionListResponse(BaseModel):
    """Response model for Position list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of Position objects"
    )
    total: int = Field(..., description="Total number of entities")


class PositionSearchResponse(BaseModel):
    """Response model for Position search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")
