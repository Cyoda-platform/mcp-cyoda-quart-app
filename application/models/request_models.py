"""
Request models for Pet Store Performance Analysis Application API.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ProductQueryParams(BaseModel):
    """Query parameters for Product listing endpoints."""
    category: Optional[str] = Field(None, description="Filter by product category")
    status: Optional[str] = Field(None, description="Filter by product status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class ProductUpdateQueryParams(BaseModel):
    """Query parameters for Product update endpoints."""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class ReportQueryParams(BaseModel):
    """Query parameters for Report listing endpoints."""
    report_type: Optional[str] = Field(None, alias="reportType", description="Filter by report type")
    email_status: Optional[str] = Field(None, alias="emailStatus", description="Filter by email status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for Report update endpoints."""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class DataExtractionQueryParams(BaseModel):
    """Query parameters for DataExtraction listing endpoints."""
    extraction_type: Optional[str] = Field(None, alias="extractionType", description="Filter by extraction type")
    extraction_status: Optional[str] = Field(None, alias="extractionStatus", description="Filter by extraction status")
    api_source: Optional[str] = Field(None, alias="apiSource", description="Filter by API source")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class DataExtractionUpdateQueryParams(BaseModel):
    """Query parameters for DataExtraction update endpoints."""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class SearchRequest(BaseModel):
    """Generic search request model."""
    name: Optional[str] = Field(None, description="Search by name")
    category: Optional[str] = Field(None, description="Search by category")
    status: Optional[str] = Field(None, description="Search by status")
    state: Optional[str] = Field(None, description="Search by workflow state")


class TransitionRequest(BaseModel):
    """Request model for workflow transitions."""
    transition_name: str = Field(..., alias="transitionName", description="Name of transition to execute")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
