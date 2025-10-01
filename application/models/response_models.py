"""
Response Models for Pet API endpoints.

Provides comprehensive response models for all Pet API operations including
entity responses, list responses, and operation result models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PetResponse(BaseModel):
    """Response model for single Pet operations."""

    id: Optional[str] = Field(default=None, description="Pet technical ID")
    entity_id: Optional[str] = Field(default=None, description="Pet entity ID")
    name: str = Field(..., description="Pet name")
    status: Optional[str] = Field(default=None, description="Pet status")
    breed: Optional[str] = Field(default=None, description="Pet breed")
    category: Optional[Dict[str, Any]] = Field(default=None, description="Pet category")
    photo_urls: Optional[List[str]] = Field(
        default=None, alias="photoUrls", description="Pet photo URLs"
    )
    tags: Optional[List[Dict[str, Any]]] = Field(default=None, description="Pet tags")
    price: Optional[float] = Field(default=None, description="Pet price")
    age: Optional[int] = Field(default=None, description="Pet age")
    description: Optional[str] = Field(default=None, description="Pet description")
    inventory_count: Optional[int] = Field(
        default=None, alias="inventoryCount", description="Inventory count"
    )
    state: Optional[str] = Field(default=None, description="Workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )


class PetListResponse(BaseModel):
    """Response model for Pet list operations."""

    pets: List[Dict[str, Any]] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class PetSearchResponse(BaseModel):
    """Response model for Pet search operations."""

    pets: List[Dict[str, Any]] = Field(..., description="List of matching pets")
    total: int = Field(..., description="Total number of matching pets")
    search_criteria: Optional[Dict[str, Any]] = Field(
        default=None, alias="searchCriteria", description="Applied search criteria"
    )


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Operation result message")
    entity_id: str = Field(..., description="ID of the deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence check operations."""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(..., description="Entity ID that was checked")


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count of entities")
    entity_type: Optional[str] = Field(
        default=None, description="Type of entities counted"
    )


class TransitionResponse(BaseModel):
    """Response model for workflow transition operations."""

    id: str = Field(..., description="Entity technical ID")
    message: str = Field(..., description="Transition result message")
    previous_state: Optional[str] = Field(
        default=None, alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")
    transition_name: Optional[str] = Field(
        default=None, alias="transitionName", description="Name of executed transition"
    )


class TransitionsResponse(BaseModel):
    """Response model for available transitions query."""

    entity_id: str = Field(..., description="Entity ID")
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current workflow state"
    )
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="List of available transitions"
    )


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""

    error: str = Field(..., description="Validation error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    field_errors: Optional[Dict[str, List[str]]] = Field(
        default=None, alias="fieldErrors", description="Field-specific validation errors"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
