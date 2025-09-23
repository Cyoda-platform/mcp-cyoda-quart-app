# models/response_models.py

"""
Response models for Pet Store Performance Analysis System API
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    """Response model for single product"""

    # This will be populated with the actual Product entity data
    pass


class ProductListResponse(BaseModel):
    """Response model for product list"""

    products: List[Dict[str, Any]] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")


class ProductSearchResponse(BaseModel):
    """Response model for product search"""

    products: List[Dict[str, Any]] = Field(..., description="List of matching products")
    total: int = Field(..., description="Total number of matching products")


class ReportResponse(BaseModel):
    """Response model for single report"""

    # This will be populated with the actual Report entity data
    pass


class ReportListResponse(BaseModel):
    """Response model for report list"""

    reports: List[Dict[str, Any]] = Field(..., description="List of reports")
    total: int = Field(..., description="Total number of reports")


class ReportSearchResponse(BaseModel):
    """Response model for report search"""

    reports: List[Dict[str, Any]] = Field(..., description="List of matching reports")
    total: int = Field(..., description="Total number of matching reports")


class DataExtractionResponse(BaseModel):
    """Response model for single data extraction"""

    # This will be populated with the actual DataExtraction entity data
    pass


class DataExtractionListResponse(BaseModel):
    """Response model for data extraction list"""

    extractions: List[Dict[str, Any]] = Field(
        ..., description="List of data extractions"
    )
    total: int = Field(..., description="Total number of data extractions")


class DataExtractionSearchResponse(BaseModel):
    """Response model for data extraction search"""

    extractions: List[Dict[str, Any]] = Field(
        ..., description="List of matching data extractions"
    )
    total: int = Field(..., description="Total number of matching data extractions")


class CountResponse(BaseModel):
    """Response model for count operations"""

    count: int = Field(..., description="Total count")


class DeleteResponse(BaseModel):
    """Response model for delete operations"""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Success or error message")
    entity_id: str = Field(
        ..., alias="entityId", description="ID of the deleted entity"
    )


class ErrorResponse(BaseModel):
    """Response model for errors"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors"""

    error: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class ExistsResponse(BaseModel):
    """Response model for existence checks"""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(..., alias="entityId", description="ID of the entity")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Success message")
    previous_state: Optional[str] = Field(
        None, alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    current_state: Optional[str] = Field(
        None, alias="currentState", description="Current workflow state"
    )
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="List of available transitions"
    )
