"""
Request and Response Models for ExampleEntity and OtherEntity API endpoints.

Provides comprehensive validation models for all API operations including
query parameters, request bodies, and response schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# from common.models.base import BaseValidatedModel  # Not needed for basic models


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    code: Optional[str] = Field(default=None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class EntityResponse(BaseModel):
    """Response model for single entity operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: str = Field(..., description="Technical ID from Cyoda")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class EntityListResponse(BaseModel):
    """Response model for entity list operations."""

    entities: List[Dict[str, Any]] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of entities")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


# ExampleEntity specific models
class ExampleEntityQueryParams(BaseModel):
    """Query parameters for ExampleEntity endpoints."""

    category: Optional[str] = Field(
        default=None, description="Filter by category", pattern=r"^[A-Z_]+$"
    )
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Filter by active status"
    )
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_categories = ["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"]
        if v not in allowed_categories:
            raise ValueError(f"Category must be one of: {allowed_categories}")
        return v


class ExampleEntityUpdateQueryParams(BaseModel):
    """Query parameters for ExampleEntity update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


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
            "transition_to_processed",
            "transition_to_validated",
            "transition_to_completed",
            "transition_to_archived",
        ]
        if v not in allowed_transitions:
            raise ValueError(f"Transition must be one of: {allowed_transitions}")
        return v


class SearchRequest(BaseModel):
    """Request model for entity search operations."""

    category: Optional[str] = Field(default=None, description="Filter by category")
    name: Optional[str] = Field(default=None, description="Filter by name")
    state: Optional[str] = Field(default=None, description="Filter by state")
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Filter by active status"
    )


class OtherEntitySearchRequest(BaseModel):
    """Request model for OtherEntity search operations."""

    title: Optional[str] = Field(default=None, description="Filter by title")
    content: Optional[str] = Field(default=None, description="Filter by content")
    priority: Optional[str] = Field(default=None, description="Filter by priority")
    source_entity_id: Optional[str] = Field(
        default=None, alias="sourceEntityId", description="Filter by source entity ID"
    )
    state: Optional[str] = Field(default=None, description="Filter by state")


# OtherEntity specific models
class OtherEntityQueryParams(BaseModel):
    """Query parameters for OtherEntity endpoints."""

    source_entity_id: Optional[str] = Field(
        default=None,
        alias="sourceEntityId",
        description="Filter by source entity ID",
        pattern=r"^[a-fA-F0-9-]+$",
    )
    priority: Optional[str] = Field(
        default=None, description="Filter by priority level", pattern=r"^(LOW|MEDIUM|HIGH)$"
    )
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_priorities = ["LOW", "MEDIUM", "HIGH"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class OtherEntityUpdateQueryParams(BaseModel):
    """Query parameters for OtherEntity update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Path parameter models
class EntityIdParam(BaseModel):
    """Path parameter model for entity ID validation."""

    entity_id: str = Field(
        ...,
        description="Entity identifier",
        pattern=r"^[a-fA-F0-9-]+$",
        min_length=1,
        max_length=100,
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Entity ID must be a non-empty string")
        return v.strip()
