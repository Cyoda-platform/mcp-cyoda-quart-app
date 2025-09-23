"""
Request models for Weather Data Application API.

Provides Pydantic models for request validation and documentation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class WeatherStationQueryParams(BaseModel):
    """Query parameters for listing weather stations."""

    province: Optional[str] = Field(
        default=None, description="Filter by province/territory"
    )
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of results to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class WeatherStationUpdateQueryParams(BaseModel):
    """Query parameters for updating weather stations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to execute"
    )


class WeatherDataQueryParams(BaseModel):
    """Query parameters for listing weather data."""

    station_id: Optional[str] = Field(
        default=None, alias="stationId", description="Filter by station ID"
    )
    observation_date: Optional[str] = Field(
        default=None,
        alias="observationDate",
        description="Filter by observation date (YYYY-MM-DD)",
    )
    observation_type: Optional[str] = Field(
        default=None,
        alias="observationType",
        description="Filter by observation type (daily, monthly, hourly)",
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of results to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class WeatherDataUpdateQueryParams(BaseModel):
    """Query parameters for updating weather data."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to execute"
    )


class WeatherSearchRequest(BaseModel):
    """Request model for weather data search."""

    station_id: Optional[str] = Field(
        default=None, alias="stationId", description="Station ID to search for"
    )
    province: Optional[str] = Field(default=None, description="Province to search in")
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Active status filter"
    )
    observation_date: Optional[str] = Field(
        default=None, alias="observationDate", description="Observation date filter"
    )


class TransitionRequest(BaseModel):
    """Request model for workflow transitions."""

    transition_name: str = Field(
        ...,
        alias="transitionName",
        description="Name of the workflow transition to execute",
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
