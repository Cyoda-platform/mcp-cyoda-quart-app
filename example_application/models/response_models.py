"""
Response Models for ExampleEntity and OtherEntity API endpoints.

Provides comprehensive response schemas for all API operations with proper
validation and documentation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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


# ExampleEntity Response Models
class ExampleEntityResponse(BaseModel):
    """Response model for ExampleEntity operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    name: str = Field(..., description="Entity name")
    description: str = Field(..., description="Entity description")
    value: float = Field(..., description="Numeric value")
    category: str = Field(..., description="Entity category")
    is_active: bool = Field(..., alias="isActive", description="Active status")
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )
    version: str = Field(..., description="Entity version")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Entity metadata"
    )
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None, alias="processedData", description="Processed data from workflows"
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None, alias="validationResult", description="Validation results"
    )


class ExampleEntityListResponse(BaseModel):
    """Response model for ExampleEntity list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of ExampleEntity objects"
    )
    total: int = Field(..., description="Total number of entities")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class ExampleEntitySearchResponse(BaseModel):
    """Response model for ExampleEntity search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching entities")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied search query"
    )


# OtherEntity Response Models
class OtherEntityResponse(BaseModel):
    """Response model for OtherEntity operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    title: str = Field(..., description="Entity title")
    content: str = Field(..., description="Entity content")
    priority: str = Field(..., description="Priority level")
    source_entity_id: Optional[str] = Field(
        default=None, alias="sourceEntityId", description="Source entity reference"
    )
    last_updated_by: Optional[str] = Field(
        default=None, alias="lastUpdatedBy", description="Last updated by reference"
    )
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )
    version: str = Field(..., description="Entity version")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Entity metadata"
    )


class OtherEntityListResponse(BaseModel):
    """Response model for OtherEntity list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of OtherEntity objects"
    )
    total: int = Field(..., description="Total number of entities")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


# Workflow Response Models
class TransitionResponse(BaseModel):
    """Response model for workflow transition operations."""

    entity_id: str = Field(..., description="Entity ID")
    transition_name: str = Field(
        ..., alias="transitionName", description="Executed transition"
    )
    previous_state: str = Field(
        ..., alias="previousState", description="Previous workflow state"
    )
    current_state: str = Field(
        ..., alias="currentState", description="Current workflow state"
    )
    success: bool = Field(..., description="Transition success status")
    message: Optional[str] = Field(
        default=None, description="Transition result message"
    )
    timestamp: Optional[str] = Field(default=None, description="Transition timestamp")


class WorkflowStateResponse(BaseModel):
    """Response model for workflow state information."""

    entity_id: str = Field(..., description="Entity ID")
    current_state: str = Field(
        ..., alias="currentState", description="Current workflow state"
    )
    available_transitions: List[str] = Field(
        ...,
        alias="availableTransitions",
        description="Available transitions from current state",
    )
    state_metadata: Optional[Dict[str, Any]] = Field(
        default=None, alias="stateMetadata", description="State-specific metadata"
    )


# Health and Status Response Models
class HealthResponse(BaseModel):
    """Response model for health check endpoints."""

    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    dependencies: Optional[Dict[str, str]] = Field(
        default=None, description="Dependency health status"
    )


class StatusResponse(BaseModel):
    """Response model for service status endpoints."""

    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    uptime: Optional[str] = Field(default=None, description="Service uptime")
    metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Service metrics"
    )


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
