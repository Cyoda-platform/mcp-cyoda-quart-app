# models/request_models.py

"""
Request models for Pet Store Performance Analysis System API
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProductQueryParams(BaseModel):
    """Query parameters for listing products"""

    category: Optional[str] = Field(None, description="Filter by category name")
    status: Optional[str] = Field(None, description="Filter by product status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    performance_score_min: Optional[float] = Field(
        None, alias="performanceScoreMin", description="Minimum performance score"
    )
    performance_score_max: Optional[float] = Field(
        None, alias="performanceScoreMax", description="Maximum performance score"
    )
    trend_indicator: Optional[str] = Field(
        None, alias="trendIndicator", description="Filter by trend indicator"
    )
    restock_needed: Optional[bool] = Field(
        None, alias="restockNeeded", description="Filter by restock needed flag"
    )
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class ProductUpdateQueryParams(BaseModel):
    """Query parameters for updating products"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class ReportQueryParams(BaseModel):
    """Query parameters for listing reports"""

    report_type: Optional[str] = Field(
        None, alias="reportType", description="Filter by report type"
    )
    email_status: Optional[str] = Field(
        None, alias="emailStatus", description="Filter by email status"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    period_start: Optional[str] = Field(
        None, alias="periodStart", description="Filter by period start date"
    )
    period_end: Optional[str] = Field(
        None, alias="periodEnd", description="Filter by period end date"
    )
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for updating reports"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class DataExtractionQueryParams(BaseModel):
    """Query parameters for listing data extractions"""

    job_type: Optional[str] = Field(
        None, alias="jobType", description="Filter by job type"
    )
    execution_status: Optional[str] = Field(
        None, alias="executionStatus", description="Filter by execution status"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    scheduled_after: Optional[str] = Field(
        None, alias="scheduledAfter", description="Filter by scheduled time (after)"
    )
    scheduled_before: Optional[str] = Field(
        None, alias="scheduledBefore", description="Filter by scheduled time (before)"
    )
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class DataExtractionUpdateQueryParams(BaseModel):
    """Query parameters for updating data extractions"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class SearchRequest(BaseModel):
    """Generic search request model"""

    name: Optional[str] = Field(None, description="Search by name")
    category: Optional[str] = Field(None, description="Search by category")
    status: Optional[str] = Field(None, description="Search by status")
    state: Optional[str] = Field(None, description="Search by workflow state")

    # Product-specific search fields
    performance_score_min: Optional[float] = Field(None, alias="performanceScoreMin")
    performance_score_max: Optional[float] = Field(None, alias="performanceScoreMax")
    trend_indicator: Optional[str] = Field(None, alias="trendIndicator")
    restock_needed: Optional[bool] = Field(None, alias="restockNeeded")

    # Report-specific search fields
    report_type: Optional[str] = Field(None, alias="reportType")
    email_status: Optional[str] = Field(None, alias="emailStatus")

    # DataExtraction-specific search fields
    job_type: Optional[str] = Field(None, alias="jobType")
    execution_status: Optional[str] = Field(None, alias="executionStatus")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to trigger"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for the transition"
    )
