"""
Response models for Cat Fact Subscription Application.

Provides response models for API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SubscriberResponse(BaseModel):
    """Response model for single subscriber"""
    data: Dict[str, Any]


class SubscriberListResponse(BaseModel):
    """Response model for subscriber list"""
    entities: List[Dict[str, Any]]
    total: int


class SubscriberSearchResponse(BaseModel):
    """Response model for subscriber search"""
    entities: List[Dict[str, Any]]
    total: int


class CatFactResponse(BaseModel):
    """Response model for single cat fact"""
    data: Dict[str, Any]


class CatFactListResponse(BaseModel):
    """Response model for cat fact list"""
    entities: List[Dict[str, Any]]
    total: int


class CatFactSearchResponse(BaseModel):
    """Response model for cat fact search"""
    entities: List[Dict[str, Any]]
    total: int


class EmailCampaignResponse(BaseModel):
    """Response model for single email campaign"""
    data: Dict[str, Any]


class EmailCampaignListResponse(BaseModel):
    """Response model for email campaign list"""
    entities: List[Dict[str, Any]]
    total: int


class EmailCampaignSearchResponse(BaseModel):
    """Response model for email campaign search"""
    entities: List[Dict[str, Any]]
    total: int


class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    success: bool
    message: str
    entity_id: str = Field(alias="entityId")


class ExistsResponse(BaseModel):
    """Response model for existence checks"""
    exists: bool
    entity_id: str = Field(alias="entityId")


class CountResponse(BaseModel):
    """Response model for count operations"""
    count: int


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""
    entity_id: str = Field(alias="entityId")
    available_transitions: List[str] = Field(alias="availableTransitions")
    current_state: Optional[str] = Field(default=None, alias="currentState")


class TransitionResponse(BaseModel):
    """Response model for transition execution"""
    id: str
    message: str
    previous_state: str = Field(alias="previousState")
    new_state: str = Field(alias="newState")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response model"""
    error: str
    code: str = "VALIDATION_ERROR"
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str


class StatusResponse(BaseModel):
    """Status response model"""
    status: str
    message: str
