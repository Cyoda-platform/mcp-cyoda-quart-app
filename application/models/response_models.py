"""
Response models for Pet Store Performance Analysis Application API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    """Response model for single Product entity."""
    id: str = Field(..., description="Product technical ID")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    status: str = Field(..., description="Product status")
    state: str = Field(..., description="Workflow state")
    salesVolume: Optional[int] = Field(None, description="Sales volume")
    revenue: Optional[float] = Field(None, description="Revenue")
    stockLevel: Optional[int] = Field(None, description="Stock level")
    performanceScore: Optional[float] = Field(None, description="Performance score")


class ProductListResponse(BaseModel):
    """Response model for Product entity lists."""
    entities: List[Dict[str, Any]] = Field(..., description="List of Product entities")
    total: int = Field(..., description="Total number of entities")


class ProductSearchResponse(BaseModel):
    """Response model for Product search results."""
    entities: List[Dict[str, Any]] = Field(..., description="List of matching Product entities")
    total: int = Field(..., description="Total number of matching entities")


class ReportResponse(BaseModel):
    """Response model for single Report entity."""
    id: str = Field(..., description="Report technical ID")
    title: str = Field(..., description="Report title")
    reportType: str = Field(..., description="Report type")
    state: str = Field(..., description="Workflow state")
    emailStatus: Optional[str] = Field(None, description="Email dispatch status")
    generatedAt: Optional[str] = Field(None, description="Generation timestamp")
    totalRevenue: Optional[float] = Field(None, description="Total revenue")
    totalSalesVolume: Optional[int] = Field(None, description="Total sales volume")


class ReportListResponse(BaseModel):
    """Response model for Report entity lists."""
    entities: List[Dict[str, Any]] = Field(..., description="List of Report entities")
    total: int = Field(..., description="Total number of entities")


class ReportSearchResponse(BaseModel):
    """Response model for Report search results."""
    entities: List[Dict[str, Any]] = Field(..., description="List of matching Report entities")
    total: int = Field(..., description="Total number of matching entities")


class DataExtractionResponse(BaseModel):
    """Response model for single DataExtraction entity."""
    id: str = Field(..., description="DataExtraction technical ID")
    jobName: str = Field(..., description="Job name")
    apiSource: str = Field(..., description="API source")
    extractionType: str = Field(..., description="Extraction type")
    extractionStatus: str = Field(..., description="Extraction status")
    state: str = Field(..., description="Workflow state")
    recordsExtracted: Optional[int] = Field(None, description="Records extracted")
    recordsProcessed: Optional[int] = Field(None, description="Records processed")


class DataExtractionListResponse(BaseModel):
    """Response model for DataExtraction entity lists."""
    entities: List[Dict[str, Any]] = Field(..., description="List of DataExtraction entities")
    total: int = Field(..., description="Total number of entities")


class DataExtractionSearchResponse(BaseModel):
    """Response model for DataExtraction search results."""
    entities: List[Dict[str, Any]] = Field(..., description="List of matching DataExtraction entities")
    total: int = Field(..., description="Total number of matching entities")


class CountResponse(BaseModel):
    """Response model for entity count operations."""
    count: int = Field(..., description="Total count of entities")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success or error message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for entity existence checks."""
    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., alias="entityId", description="Entity ID that was checked")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""
    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previousState: str = Field(..., description="Previous workflow state")
    newState: str = Field(..., description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""
    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(..., alias="availableTransitions", description="Available transitions")
    current_state: Optional[str] = Field(None, alias="currentState", description="Current workflow state")


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    error: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
