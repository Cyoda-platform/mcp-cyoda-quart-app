"""
Response models for Weather Data Application API.

Provides Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WeatherStationResponse(BaseModel):
    """Response model for a single weather station."""
    
    entity_id: Optional[str] = Field(default=None, description="Entity ID")
    technical_id: Optional[str] = Field(default=None, description="Technical ID")
    station_id: str = Field(..., description="Station identifier")
    station_name: str = Field(..., description="Station name")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    elevation: Optional[float] = Field(default=None, description="Elevation in meters")
    province: Optional[str] = Field(default=None, description="Province")
    country: str = Field(default="Canada", description="Country")
    station_type: Optional[str] = Field(default=None, description="Station type")
    is_active: bool = Field(default=True, description="Active status")
    first_year: Optional[int] = Field(default=None, description="First year of data")
    last_year: Optional[int] = Field(default=None, description="Last year of data")
    state: Optional[str] = Field(default=None, description="Workflow state")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")


class WeatherStationListResponse(BaseModel):
    """Response model for a list of weather stations."""
    
    stations: List[WeatherStationResponse] = Field(..., description="List of weather stations")
    total: int = Field(..., description="Total number of stations")


class WeatherDataResponse(BaseModel):
    """Response model for a single weather data record."""
    
    entity_id: Optional[str] = Field(default=None, description="Entity ID")
    technical_id: Optional[str] = Field(default=None, description="Technical ID")
    station_id: str = Field(..., description="Station identifier")
    observation_date: str = Field(..., description="Observation date")
    observation_type: str = Field(default="daily", description="Observation type")
    temperature_max: Optional[float] = Field(default=None, description="Maximum temperature (°C)")
    temperature_min: Optional[float] = Field(default=None, description="Minimum temperature (°C)")
    temperature_mean: Optional[float] = Field(default=None, description="Mean temperature (°C)")
    precipitation_total: Optional[float] = Field(default=None, description="Total precipitation (mm)")
    rain_total: Optional[float] = Field(default=None, description="Total rainfall (mm)")
    snow_total: Optional[float] = Field(default=None, description="Total snowfall (mm)")
    wind_speed: Optional[float] = Field(default=None, description="Wind speed (km/h)")
    wind_direction: Optional[float] = Field(default=None, description="Wind direction (degrees)")
    pressure_sea_level: Optional[float] = Field(default=None, description="Sea level pressure (kPa)")
    pressure_station: Optional[float] = Field(default=None, description="Station pressure (kPa)")
    humidity: Optional[float] = Field(default=None, description="Humidity (%)")
    visibility: Optional[float] = Field(default=None, description="Visibility (km)")
    data_quality: Optional[str] = Field(default=None, description="Data quality assessment")
    state: Optional[str] = Field(default=None, description="Workflow state")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")
    data_completeness_score: Optional[float] = Field(default=None, description="Data completeness score")


class WeatherDataListResponse(BaseModel):
    """Response model for a list of weather data records."""
    
    weather_data: List[WeatherDataResponse] = Field(..., description="List of weather data records")
    total: int = Field(..., description="Total number of records")


class CountResponse(BaseModel):
    """Response model for count operations."""
    
    count: int = Field(..., description="Number of entities")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks."""
    
    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., description="Entity ID that was checked")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""
    
    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition message")
    previous_state: Optional[str] = Field(default=None, description="Previous workflow state")
    new_state: str = Field(..., description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""
    
    entity_id: str = Field(..., description="Entity ID")
    available_transitions: List[str] = Field(..., description="Available transition names")
    current_state: Optional[str] = Field(default=None, description="Current workflow state")


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    
    error: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
