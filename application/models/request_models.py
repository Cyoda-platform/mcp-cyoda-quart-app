"""
Request Models for Booking and Report API endpoints.

Provides comprehensive validation models for all API operations including
query parameters, request bodies, and search criteria.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class BookingQueryParams(BaseModel):
    """Query parameters for booking list endpoint."""

    firstname: Optional[str] = Field(default=None, description="Filter by guest first name")
    lastname: Optional[str] = Field(default=None, description="Filter by guest last name")
    depositpaid: Optional[bool] = Field(default=None, description="Filter by deposit payment status")
    min_price: Optional[int] = Field(default=None, alias="minPrice", description="Minimum total price filter")
    max_price: Optional[int] = Field(default=None, alias="maxPrice", description="Maximum total price filter")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Filter by check-in date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="Filter by check-in date (YYYY-MM-DD)")
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Maximum number of results to return")
    offset: int = Field(default=0, description="Number of results to skip")

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v


class BookingUpdateQueryParams(BaseModel):
    """Query parameters for booking update endpoint."""

    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")


class ReportQueryParams(BaseModel):
    """Query parameters for report list endpoint."""

    report_type: Optional[str] = Field(default=None, alias="reportType", description="Filter by report type")
    display_format: Optional[str] = Field(default=None, alias="displayFormat", description="Filter by display format")
    generated_by: Optional[str] = Field(default=None, alias="generatedBy", description="Filter by generator")
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Maximum number of results to return")
    offset: int = Field(default=0, description="Number of results to skip")

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for report update endpoint."""

    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")


class SearchRequest(BaseModel):
    """Generic search request model."""

    firstname: Optional[str] = Field(default=None, description="Search by first name")
    lastname: Optional[str] = Field(default=None, description="Search by last name")
    depositpaid: Optional[bool] = Field(default=None, description="Search by deposit status")
    totalprice: Optional[int] = Field(default=None, description="Search by total price")
    state: Optional[str] = Field(default=None, description="Search by workflow state")


class BookingFilterRequest(BaseModel):
    """Request model for booking filtering operations."""

    depositpaid: Optional[bool] = Field(default=None, description="Filter by deposit payment status")
    min_price: Optional[int] = Field(default=None, alias="minPrice", description="Minimum total price")
    max_price: Optional[int] = Field(default=None, alias="maxPrice", description="Maximum total price")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start date for check-in filter (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End date for check-in filter (YYYY-MM-DD)")
    firstname: Optional[str] = Field(default=None, description="Filter by guest first name")
    lastname: Optional[str] = Field(default=None, description="Filter by guest last name")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class ReportGenerationRequest(BaseModel):
    """Request model for report generation."""

    title: str = Field(..., description="Title of the report")
    description: Optional[str] = Field(default=None, description="Description of the report")
    report_type: str = Field(..., alias="reportType", description="Type of report to generate")
    display_format: str = Field(default="table", alias="displayFormat", description="Display format for the report")
    filter_criteria: Optional[Dict[str, Any]] = Field(default=None, alias="filterCriteria", description="Filter criteria for the report")

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        allowed_types = ["summary", "filtered", "date_range", "custom"]
        if v not in allowed_types:
            raise ValueError(f"Report type must be one of: {allowed_types}")
        return v

    @field_validator("display_format")
    @classmethod
    def validate_display_format(cls, v: str) -> str:
        allowed_formats = ["table", "chart", "json", "csv"]
        if v not in allowed_formats:
            raise ValueError(f"Display format must be one of: {allowed_formats}")
        return v


class TransitionRequest(BaseModel):
    """Request model for workflow transitions."""

    transition_name: str = Field(..., alias="transitionName", description="Name of the transition to execute")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters for the transition")


class BulkOperationRequest(BaseModel):
    """Request model for bulk operations."""

    entity_ids: list[str] = Field(..., alias="entityIds", description="List of entity IDs to operate on")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters for the operation")

    @field_validator("entity_ids")
    @classmethod
    def validate_entity_ids(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Entity IDs list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot operate on more than 100 entities at once")
        return v
