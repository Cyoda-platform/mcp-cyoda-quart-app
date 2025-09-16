"""
Request models for Application API endpoints.

Provides Pydantic models for request validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class TransitionRequest(BaseModel):
    """Request model for workflow transitions."""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


class SearchRequest(BaseModel):
    """Request model for entity search operations."""

    userId: Optional[str] = Field(None, description="Filter by user ID")
    eggType: Optional[str] = Field(None, description="Filter by egg type")
    isActive: Optional[bool] = Field(None, description="Filter by active status")
    state: Optional[str] = Field(None, description="Filter by entity state")
    username: Optional[str] = Field(None, description="Filter by username")
    email: Optional[str] = Field(None, description="Filter by email")


class EggAlarmQueryParams(BaseModel):
    """Query parameters for EggAlarm list endpoint."""

    userId: Optional[str] = Field(None, description="Filter by user ID")
    eggType: Optional[str] = Field(None, description="Filter by egg type")
    isActive: Optional[bool] = Field(None, description="Filter by active status")
    state: Optional[str] = Field(None, description="Filter by entity state")
    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of results"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class EggAlarmUpdateQueryParams(BaseModel):
    """Query parameters for EggAlarm update endpoint."""

    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


class UserQueryParams(BaseModel):
    """Query parameters for User list endpoint."""

    username: Optional[str] = Field(None, description="Filter by username")
    email: Optional[str] = Field(None, description="Filter by email")
    state: Optional[str] = Field(None, description="Filter by entity state")
    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of results"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class UserUpdateQueryParams(BaseModel):
    """Query parameters for User update endpoint."""

    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )
