"""
Response models for Application API endpoints.

Provides Pydantic models for response validation and documentation.
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
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Validation details")


class DeleteResponse(BaseModel):
    """Response model for delete operations"""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks"""

    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., alias="entityId", description="Entity ID checked")


class CountResponse(BaseModel):
    """Response model for count operations"""

    count: int = Field(..., description="Total count")


class TransitionResponse(BaseModel):
    """Response model for transition operations"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Success message")
    previous_state: Optional[str] = Field(
        None, alias="previousState", description="Previous workflow state"
    )
    new_state: Optional[str] = Field(
        None, alias="newState", description="New workflow state"
    )


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="List of available transitions"
    )
    current_state: Optional[str] = Field(
        None, alias="currentState", description="Current workflow state"
    )


# DataSource response models
class DataSourceResponse(BaseModel):
    """Response model for single DataSource"""

    class Config:
        extra = "allow"


class DataSourceListResponse(BaseModel):
    """Response model for DataSource list"""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of DataSource entities"
    )
    total: int = Field(..., description="Total count")


class DataSourceSearchResponse(BaseModel):
    """Response model for DataSource search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")


# DataAnalysis response models
class DataAnalysisResponse(BaseModel):
    """Response model for single DataAnalysis"""

    class Config:
        extra = "allow"


class DataAnalysisListResponse(BaseModel):
    """Response model for DataAnalysis list"""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of DataAnalysis entities"
    )
    total: int = Field(..., description="Total count")


class DataAnalysisSearchResponse(BaseModel):
    """Response model for DataAnalysis search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")


# Report response models
class ReportResponse(BaseModel):
    """Response model for single Report"""

    class Config:
        extra = "allow"


class ReportListResponse(BaseModel):
    """Response model for Report list"""

    entities: List[Dict[str, Any]] = Field(..., description="List of Report entities")
    total: int = Field(..., description="Total count")


class ReportSearchResponse(BaseModel):
    """Response model for Report search"""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results count")
