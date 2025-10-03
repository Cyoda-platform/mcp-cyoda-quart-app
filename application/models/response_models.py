"""
Response models for Pet Hamster Application API.

Provides Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PetHamsterResponse(BaseModel):
    """Response model for a single pet hamster."""

    id: str = Field(..., description="Technical ID of the hamster")
    name: str = Field(..., description="Name of the hamster")
    breed: Optional[str] = Field(default=None, description="Breed of the hamster")
    age_months: Optional[int] = Field(
        default=None, alias="ageMonths", description="Age in months"
    )
    mood: Optional[str] = Field(default=None, description="Current mood")
    activity_level: Optional[str] = Field(
        default=None, alias="activityLevel", description="Current activity level"
    )
    is_safe_to_handle: Optional[bool] = Field(
        default=None, alias="isSafeToHandle", description="Safety status for handling"
    )
    current_location: Optional[str] = Field(
        default=None, alias="currentLocation", description="Current location"
    )
    interaction_count: Optional[int] = Field(
        default=None, alias="interactionCount", description="Total interaction count"
    )
    last_interaction_result: Optional[str] = Field(
        default=None,
        alias="lastInteractionResult",
        description="Result of last interaction",
    )
    state: Optional[str] = Field(default=None, description="Workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )


class PetHamsterListResponse(BaseModel):
    """Response model for a list of pet hamsters."""

    entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of pet hamster entities"
    )
    total: int = Field(..., description="Total number of entities")


class PetHamsterSearchResponse(BaseModel):
    """Response model for pet hamster search results."""

    entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of matching pet hamster entities"
    )
    total: int = Field(..., description="Total number of matching entities")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(default=True, description="Success indicator")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks."""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(
        ..., alias="entityId", description="Entity ID that was checked"
    )


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count of entities")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previous_state: Optional[str] = Field(
        default=None, alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        default_factory=list,
        alias="availableTransitions",
        description="List of available transition names",
    )
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current workflow state"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response."""

    error: str = Field(..., description="Validation error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional validation error details"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")


class StatusResponse(BaseModel):
    """Status response."""

    status: str = Field(..., description="Current status")
    message: Optional[str] = Field(default=None, description="Status message")


class WorkflowStateResponse(BaseModel):
    """Workflow state response."""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    current_state: str = Field(..., alias="currentState", description="Current state")
    available_transitions: List[str] = Field(
        default_factory=list,
        alias="availableTransitions",
        description="Available transitions",
    )
