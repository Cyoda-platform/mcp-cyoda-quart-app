"""
WeatherData Entity for Weather Data Application

Represents weather observations and measurements from MSC GeoMet API.
Stores daily weather data including temperature, precipitation, and other meteorological measurements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class WeatherData(CyodaEntity):
    """
    WeatherData represents weather observations from MSC GeoMet API.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> collected -> validated -> processed -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeatherData"
    ENTITY_VERSION: ClassVar[int] = 1

    # Reference to weather station
    station_id: str = Field(..., description="Weather station identifier")
    
    # Observation metadata
    observation_date: str = Field(..., description="Date of observation (YYYY-MM-DD format)")
    observation_type: str = Field(default="daily", description="Type of observation (daily, monthly, hourly)")
    
    # Temperature measurements (Celsius)
    temperature_max: Optional[float] = Field(
        default=None, 
        alias="temperatureMax",
        description="Maximum temperature in Celsius"
    )
    temperature_min: Optional[float] = Field(
        default=None,
        alias="temperatureMin", 
        description="Minimum temperature in Celsius"
    )
    temperature_mean: Optional[float] = Field(
        default=None,
        alias="temperatureMean",
        description="Mean temperature in Celsius"
    )
    
    # Precipitation measurements (mm)
    precipitation_total: Optional[float] = Field(
        default=None,
        alias="precipitationTotal",
        description="Total precipitation in millimeters"
    )
    rain_total: Optional[float] = Field(
        default=None,
        alias="rainTotal",
        description="Total rainfall in millimeters"
    )
    snow_total: Optional[float] = Field(
        default=None,
        alias="snowTotal",
        description="Total snowfall in millimeters"
    )
    
    # Wind measurements
    wind_speed: Optional[float] = Field(
        default=None,
        alias="windSpeed",
        description="Wind speed in km/h"
    )
    wind_direction: Optional[float] = Field(
        default=None,
        alias="windDirection",
        description="Wind direction in degrees"
    )
    
    # Pressure measurements (kPa)
    pressure_sea_level: Optional[float] = Field(
        default=None,
        alias="pressureSeaLevel",
        description="Sea level pressure in kPa"
    )
    pressure_station: Optional[float] = Field(
        default=None,
        alias="pressureStation",
        description="Station pressure in kPa"
    )
    
    # Other measurements
    humidity: Optional[float] = Field(
        default=None,
        description="Relative humidity percentage"
    )
    visibility: Optional[float] = Field(
        default=None,
        description="Visibility in kilometers"
    )
    
    # Data quality indicators
    data_quality: Optional[str] = Field(
        default=None,
        alias="dataQuality",
        description="Data quality assessment"
    )
    missing_data_flags: Optional[Dict[str, bool]] = Field(
        default_factory=dict,
        alias="missingDataFlags",
        description="Flags indicating missing data for specific measurements"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the data was collected (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the data was last updated (ISO 8601 format)",
    )
    
    # Processing metadata
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Additional processed weather data and calculations",
    )

    @field_validator("station_id")
    @classmethod
    def validate_station_id(cls, v: str) -> str:
        """Validate station ID format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Station ID must be non-empty")
        return v.strip()

    @field_validator("observation_date")
    @classmethod
    def validate_observation_date(cls, v: str) -> str:
        """Validate observation date format"""
        if not v:
            raise ValueError("Observation date is required")
        try:
            # Validate date format
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Observation date must be in YYYY-MM-DD format")
        return v

    @field_validator("temperature_max", "temperature_min", "temperature_mean")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        """Validate temperature values are reasonable"""
        if v is not None:
            if v < -60 or v > 60:
                raise ValueError("Temperature must be between -60 and 60 degrees Celsius")
        return v

    @field_validator("precipitation_total", "rain_total", "snow_total")
    @classmethod
    def validate_precipitation(cls, v: Optional[float]) -> Optional[float]:
        """Validate precipitation values are non-negative"""
        if v is not None and v < 0:
            raise ValueError("Precipitation values must be non-negative")
        return v

    @field_validator("wind_speed")
    @classmethod
    def validate_wind_speed(cls, v: Optional[float]) -> Optional[float]:
        """Validate wind speed is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Wind speed must be non-negative")
        return v

    @field_validator("humidity")
    @classmethod
    def validate_humidity(cls, v: Optional[float]) -> Optional[float]:
        """Validate humidity percentage"""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError("Humidity must be between 0 and 100 percent")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def has_temperature_data(self) -> bool:
        """Check if temperature data is available"""
        return any([
            self.temperature_max is not None,
            self.temperature_min is not None,
            self.temperature_mean is not None
        ])

    def has_precipitation_data(self) -> bool:
        """Check if precipitation data is available"""
        return any([
            self.precipitation_total is not None,
            self.rain_total is not None,
            self.snow_total is not None
        ])

    def get_data_completeness_score(self) -> float:
        """Calculate data completeness score (0.0 to 1.0)"""
        total_fields = 12  # Number of measurement fields
        available_fields = sum([
            1 for field in [
                self.temperature_max, self.temperature_min, self.temperature_mean,
                self.precipitation_total, self.rain_total, self.snow_total,
                self.wind_speed, self.wind_direction,
                self.pressure_sea_level, self.pressure_station,
                self.humidity, self.visibility
            ] if field is not None
        ])
        return available_fields / total_fields

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        data["dataCompletenessScore"] = self.get_data_completeness_score()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
