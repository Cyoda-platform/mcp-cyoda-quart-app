"""
Request models for Pet Hamster Application API.

Provides Pydantic models for request validation and documentation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PetHamsterQueryParams(BaseModel):
    """Query parameters for listing pet hamsters."""
    
    mood: Optional[str] = Field(
        default=None,
        description="Filter by hamster mood (calm, agitated, sleeping, etc.)"
    )
    is_safe_to_handle: Optional[bool] = Field(
        default=None,
        alias="isSafeToHandle",
        description="Filter by safety status for handling"
    )
    current_location: Optional[str] = Field(
        default=None,
        alias="currentLocation", 
        description="Filter by current location (cage, hand, play_area)"
    )
    state: Optional[str] = Field(
        default=None,
        description="Filter by workflow state"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    )


class PetHamsterUpdateQueryParams(BaseModel):
    """Query parameters for updating pet hamsters."""
    
    transition: Optional[str] = Field(
        default=None,
        description="Workflow transition to execute after update"
    )


class SearchRequest(BaseModel):
    """Generic search request for pet hamsters."""
    
    name: Optional[str] = Field(
        default=None,
        description="Search by hamster name"
    )
    breed: Optional[str] = Field(
        default=None,
        description="Search by hamster breed"
    )
    mood: Optional[str] = Field(
        default=None,
        description="Search by current mood"
    )
    current_location: Optional[str] = Field(
        default=None,
        alias="currentLocation",
        description="Search by current location"
    )


class TransitionRequest(BaseModel):
    """Request to trigger a workflow transition."""
    
    transition_name: str = Field(
        ...,
        alias="transitionName",
        description="Name of the transition to execute"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response."""
    
    success: bool = Field(default=True, description="Success indicator")
    message: str = Field(..., description="Success message")


class EntityIdParam(BaseModel):
    """Entity ID parameter validation."""
    
    entity_id: str = Field(..., alias="entityId", description="Entity technical ID")
