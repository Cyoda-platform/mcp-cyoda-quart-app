"""
Response models for Cat Fact Subscription Application API.

Provides Pydantic models for API response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response model"""

    error: str = Field(..., description="Validation error message")
    code: str = Field("VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Validation error details"
    )


class DeleteResponse(BaseModel):
    """Response model for delete operations"""

    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks"""

    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(
        ..., alias="entityId", description="Entity ID that was checked"
    )


class CountResponse(BaseModel):
    """Response model for count operations"""

    count: int = Field(..., description="Total count")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previous_state: Optional[str] = Field(
        None, alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="Available transitions"
    )
    current_state: Optional[str] = Field(
        None, alias="currentState", description="Current workflow state"
    )


# Subscriber response models
class SubscriberResponse(BaseModel):
    """Response model for single subscriber"""

    data: Dict[str, Any] = Field(..., description="Subscriber data")


class SubscriberListResponse(BaseModel):
    """Response model for subscriber list"""

    entities: List[Dict[str, Any]] = Field(..., description="List of subscribers")
    total: int = Field(..., description="Total count")


class SubscriberSearchResponse(BaseModel):
    """Response model for subscriber search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")


# CatFact response models
class CatFactResponse(BaseModel):
    """Response model for single cat fact"""

    data: Dict[str, Any] = Field(..., description="Cat fact data")


class CatFactListResponse(BaseModel):
    """Response model for cat fact list"""

    entities: List[Dict[str, Any]] = Field(..., description="List of cat facts")
    total: int = Field(..., description="Total count")


class CatFactSearchResponse(BaseModel):
    """Response model for cat fact search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")


# EmailCampaign response models
class EmailCampaignResponse(BaseModel):
    """Response model for single email campaign"""

    data: Dict[str, Any] = Field(..., description="Email campaign data")


class EmailCampaignListResponse(BaseModel):
    """Response model for email campaign list"""

    entities: List[Dict[str, Any]] = Field(..., description="List of email campaigns")
    total: int = Field(..., description="Total count")


class EmailCampaignSearchResponse(BaseModel):
    """Response model for email campaign search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")


# System response models
class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")


class StatusResponse(BaseModel):
    """Status response model"""

    status: str = Field(..., description="Status")
    message: str = Field(..., description="Status message")


class WorkflowStateResponse(BaseModel):
    """Workflow state response model"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    current_state: str = Field(
        ..., alias="currentState", description="Current workflow state"
    )
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="Available transitions"
    )
