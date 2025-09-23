"""
Response models for EggAlarm API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""

    error: str = Field(..., description="Validation error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Validation details"
    )


class EggAlarmResponse(BaseModel):
    """Response model for single EggAlarm"""

    # This will be populated with the actual EggAlarm data
    # The structure matches the EggAlarm entity fields
    pass


class EggAlarmListResponse(BaseModel):
    """Response model for list of EggAlarms"""

    entities: List[Dict[str, Any]] = Field(..., description="List of EggAlarm entities")
    total: int = Field(..., description="Total number of entities")


class EggAlarmSearchResponse(BaseModel):
    """Response model for EggAlarm search results"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


class DeleteResponse(BaseModel):
    """Response model for delete operations"""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks"""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(
        ..., alias="entityId", description="Entity ID that was checked"
    )


class CountResponse(BaseModel):
    """Response model for count operations"""

    count: int = Field(..., description="Number of entities")


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ...,
        alias="availableTransitions",
        description="List of available transition names",
    )
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current workflow state"
    )


class TransitionResponse(BaseModel):
    """Response model for transition execution"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Success message")
    previous_state: Optional[str] = Field(
        default=None, alias="previousState", description="Previous workflow state"
    )
    new_state: Optional[str] = Field(
        default=None, alias="newState", description="New workflow state"
    )
