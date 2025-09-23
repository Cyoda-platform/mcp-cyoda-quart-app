"""
Request and Response Models for User API endpoints.

Provides comprehensive validation models for all User API operations including
query parameters, request bodies, and response schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    code: Optional[str] = Field(default=None, description="Error code")


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


class UserResponse(BaseModel):
    """Response model for single User operations."""

    id: str = Field(..., description="User technical ID")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(default=None, description="User display name")
    timezone: str = Field(..., description="User timezone")
    notification_time: str = Field(..., description="Preferred notification time")
    active: bool = Field(..., description="Whether user account is active")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class UserListResponse(BaseModel):
    """Response model for User list operations."""

    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


class UserQueryParams(BaseModel):
    """Query parameters for User list operations."""

    email: Optional[str] = Field(default=None, description="Filter by email")
    active: Optional[bool] = Field(default=None, description="Filter by active status")
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    timezone: Optional[str] = Field(default=None, description="Filter by timezone")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_states = ["initial_state", "registered", "active", "suspended", "deleted"]
        if v not in allowed_states:
            raise ValueError(f"State must be one of: {allowed_states}")
        return v


class UserUpdateQueryParams(BaseModel):
    """Query parameters for User update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )

    @field_validator("transition")
    @classmethod
    def validate_transition(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_transitions = [
            "register_user",
            "activate_user", 
            "suspend_user",
            "reactivate_user",
            "delete_user"
        ]
        if v not in allowed_transitions:
            raise ValueError(f"Transition must be one of: {allowed_transitions}")
        return v


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions."""

    transition_name: str = Field(
        ...,
        alias="transitionName",
        description="Name of the transition to execute",
        pattern=r"^[a-z_]+$",
    )

    @field_validator("transition_name")
    @classmethod
    def validate_transition_name(cls, v: str) -> str:
        allowed_transitions = [
            "register_user",
            "activate_user", 
            "suspend_user",
            "reactivate_user",
            "delete_user"
        ]
        if v not in allowed_transitions:
            raise ValueError(f"Transition must be one of: {allowed_transitions}")
        return v


class TransitionResponse(BaseModel):
    """Response model for transition operations."""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previous_state: str = Field(..., description="Previous workflow state")
    new_state: str = Field(..., description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""

    entity_id: str = Field(..., description="Entity ID")
    available_transitions: List[str] = Field(..., description="Available transitions")
    current_state: Optional[str] = Field(default=None, description="Current state")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")
    entity_id: str = Field(..., description="ID of deleted entity")


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count")


class ExistsResponse(BaseModel):
    """Response model for existence check operations."""

    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., description="Entity ID that was checked")


class SearchRequest(BaseModel):
    """Request model for search operations."""

    email: Optional[str] = Field(default=None, description="Search by email")
    name: Optional[str] = Field(default=None, description="Search by name")
    timezone: Optional[str] = Field(default=None, description="Search by timezone")
    active: Optional[bool] = Field(default=None, description="Search by active status")
    state: Optional[str] = Field(default=None, description="Search by state")


class UserSearchResponse(BaseModel):
    """Response model for User search operations."""

    users: List[UserResponse] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
