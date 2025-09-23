"""
WeatherStation Entity for Weather Data Application

Represents weather monitoring stations from MSC GeoMet API.
Stores station metadata including location, type, and operational status.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class WeatherStation(CyodaEntity):
    """
    WeatherStation represents a weather monitoring station from MSC GeoMet API.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> registered -> validated -> active -> inactive
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeatherStation"
    ENTITY_VERSION: ClassVar[int] = 1

    # Station identification fields
    station_id: str = Field(..., description="Unique station identifier from MSC GeoMet")
    station_name: str = Field(..., description="Human-readable station name")
    
    # Location fields
    latitude: float = Field(..., description="Station latitude in decimal degrees")
    longitude: float = Field(..., description="Station longitude in decimal degrees")
    elevation: Optional[float] = Field(default=None, description="Station elevation in meters")
    
    # Administrative fields
    province: Optional[str] = Field(default=None, description="Province or territory")
    country: str = Field(default="Canada", description="Country where station is located")
    
    # Station metadata
    station_type: Optional[str] = Field(default=None, description="Type of weather station")
    is_active: bool = Field(default=True, description="Whether station is currently operational")
    
    # Data availability
    first_year: Optional[int] = Field(default=None, description="First year of available data")
    last_year: Optional[int] = Field(default=None, description="Last year of available data")
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the station was registered (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt", 
        description="Timestamp when the station was last updated (ISO 8601 format)",
    )
    
    # Processing metadata
    last_data_fetch: Optional[str] = Field(
        default=None,
        alias="lastDataFetch",
        description="Timestamp of last successful data fetch from MSC GeoMet",
    )
    data_fetch_status: Optional[str] = Field(
        default=None,
        alias="dataFetchStatus",
        description="Status of last data fetch attempt",
    )

    @field_validator("station_id")
    @classmethod
    def validate_station_id(cls, v: str) -> str:
        """Validate station ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Station ID must be non-empty")
        if len(v) > 50:
            raise ValueError("Station ID must be at most 50 characters long")
        return v.strip()

    @field_validator("station_name")
    @classmethod
    def validate_station_name(cls, v: str) -> str:
        """Validate station name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Station name must be non-empty")
        if len(v) > 200:
            raise ValueError("Station name must be at most 200 characters long")
        return v.strip()

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range"""
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range"""
        if v < -180 or v > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_data_fetch_status(self, status: str, timestamp: Optional[str] = None) -> None:
        """Set data fetch status and update timestamp"""
        self.data_fetch_status = status
        self.last_data_fetch = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_operational(self) -> bool:
        """Check if station is operational (active and in active state)"""
        return self.is_active and self.state in ["active", "validated"]

    def get_location_string(self) -> str:
        """Get formatted location string"""
        location_parts = []
        if self.province:
            location_parts.append(self.province)
        location_parts.append(self.country)
        return f"{self.latitude:.4f}, {self.longitude:.4f} ({', '.join(location_parts)})"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
