"""
Request Models for Application API endpoints.

Provides comprehensive validation models for all API operations including
query parameters, request bodies, and transition requests.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# Common Request Models
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
        if not v or len(v.strip()) == 0:
            raise ValueError("Transition name cannot be empty")
        return v.strip().lower()


class SearchRequest(BaseModel):
    """Request model for entity search operations."""

    name: Optional[str] = Field(default=None, description="Search by name")
    email: Optional[str] = Field(default=None, description="Search by email")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")


# User Request Models
class UserQueryParams(BaseModel):
    """Query parameters for User endpoints."""

    username: Optional[str] = Field(default=None, description="Filter by username")
    email: Optional[str] = Field(default=None, description="Filter by email")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class UserUpdateQueryParams(BaseModel):
    """Query parameters for User update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Role Request Models
class RoleQueryParams(BaseModel):
    """Query parameters for Role endpoints."""

    name: Optional[str] = Field(default=None, description="Filter by role name")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class RoleUpdateQueryParams(BaseModel):
    """Query parameters for Role update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Permission Request Models
class PermissionQueryParams(BaseModel):
    """Query parameters for Permission endpoints."""

    name: Optional[str] = Field(default=None, description="Filter by permission name")
    resource: Optional[str] = Field(default=None, description="Filter by resource")
    action: Optional[str] = Field(default=None, description="Filter by action")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class PermissionUpdateQueryParams(BaseModel):
    """Query parameters for Permission update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Employee Request Models
class EmployeeQueryParams(BaseModel):
    """Query parameters for Employee endpoints."""

    employee_id: Optional[str] = Field(
        default=None, description="Filter by employee ID"
    )
    email: Optional[str] = Field(default=None, description="Filter by email")
    position_id: Optional[str] = Field(default=None, description="Filter by position")
    department: Optional[str] = Field(default=None, description="Filter by department")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class EmployeeUpdateQueryParams(BaseModel):
    """Query parameters for Employee update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Position Request Models
class PositionQueryParams(BaseModel):
    """Query parameters for Position endpoints."""

    title: Optional[str] = Field(default=None, description="Filter by position title")
    department: Optional[str] = Field(default=None, description="Filter by department")
    level: Optional[str] = Field(default=None, description="Filter by level")
    is_active: Optional[bool] = Field(
        default=None, description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class PositionUpdateQueryParams(BaseModel):
    """Query parameters for Position update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )
