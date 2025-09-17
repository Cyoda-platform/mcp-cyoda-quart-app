"""
Request models for Application API endpoints.

Provides Pydantic models for request validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Generic search request model"""

    # Allow any fields for flexible searching
    class Config:
        extra = "allow"


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to trigger"
    )


# DataSource query parameters
class DataSourceQueryParams(BaseModel):
    """Query parameters for DataSource list endpoint"""

    url: Optional[str] = Field(None, description="Filter by URL")
    data_format: Optional[str] = Field(
        None, alias="dataFormat", description="Filter by data format"
    )
    status: Optional[str] = Field(None, description="Filter by status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class DataSourceUpdateQueryParams(BaseModel):
    """Query parameters for DataSource update endpoint"""

    transition: Optional[str] = Field(
        None, description="Optional workflow transition to trigger after update"
    )


# DataAnalysis query parameters
class DataAnalysisQueryParams(BaseModel):
    """Query parameters for DataAnalysis list endpoint"""

    data_source_id: Optional[str] = Field(
        None, alias="dataSourceId", description="Filter by data source ID"
    )
    analysis_type: Optional[str] = Field(
        None, alias="analysisType", description="Filter by analysis type"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class DataAnalysisUpdateQueryParams(BaseModel):
    """Query parameters for DataAnalysis update endpoint"""

    transition: Optional[str] = Field(
        None, description="Optional workflow transition to trigger after update"
    )


# Report query parameters
class ReportQueryParams(BaseModel):
    """Query parameters for Report list endpoint"""

    analysis_id: Optional[str] = Field(
        None, alias="analysisId", description="Filter by analysis ID"
    )
    delivery_status: Optional[str] = Field(
        None, alias="deliveryStatus", description="Filter by delivery status"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=1000, description="Pagination limit")


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for Report update endpoint"""

    transition: Optional[str] = Field(
        None, description="Optional workflow transition to trigger after update"
    )
