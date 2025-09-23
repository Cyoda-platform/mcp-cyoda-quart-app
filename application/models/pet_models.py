"""
Pet API Models for Cyoda Pet Search Application

Request and response models for Pet API endpoints with comprehensive validation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Request Models
class PetQueryParams(BaseModel):
    """Query parameters for listing pets with filtering."""

    species: Optional[str] = Field(
        default=None,
        description="Filter by species (dog, cat, bird, fish, rabbit, hamster, other)",
    )
    status: Optional[str] = Field(
        default=None, description="Filter by status (available, pending, sold)"
    )
    category_id: Optional[int] = Field(
        default=None, alias="categoryId", description="Filter by category ID"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum number of results to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class PetSearchRequest(BaseModel):
    """Request model for pet search with multiple criteria."""

    species: Optional[str] = Field(default=None, description="Species to search for")
    status: Optional[str] = Field(default=None, description="Status to search for")
    category_id: Optional[int] = Field(
        default=None, alias="categoryId", description="Category ID to search for"
    )
    name: Optional[str] = Field(default=None, description="Pet name to search for")


class PetUpdateQueryParams(BaseModel):
    """Query parameters for updating pets."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger after update"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions."""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to trigger"
    )


# Response Models
class PetResponse(BaseModel):
    """Response model for single pet."""

    data: Dict[str, Any] = Field(..., description="Pet entity data")


class PetListResponse(BaseModel):
    """Response model for list of pets."""

    pets: List[Dict[str, Any]] = Field(..., description="List of pet entities")
    total: int = Field(..., description="Total number of pets")


class PetSearchResponse(BaseModel):
    """Response model for pet search results."""

    pets: List[Dict[str, Any]] = Field(..., description="List of matching pet entities")
    total: int = Field(..., description="Total number of matching pets")
    search_criteria: Dict[str, Any] = Field(
        ..., alias="searchCriteria", description="Search criteria used"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""

    error: str = Field(..., description="Validation error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional validation error details"
    )


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(
        ..., alias="entityId", description="ID of the deleted entity"
    )


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count of entities")


class ExistsResponse(BaseModel):
    """Response model for existence checks."""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(
        ..., alias="entityId", description="ID of the entity checked"
    )


class TransitionResponse(BaseModel):
    """Response model for transition operations."""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Success message")
    previous_state: Optional[str] = Field(
        default=None, alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ...,
        alias="availableTransitions",
        description="List of available transition names",
    )
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current workflow state"
    )
