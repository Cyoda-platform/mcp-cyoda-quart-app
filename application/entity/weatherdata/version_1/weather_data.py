# entity/weatherdata/version_1/weather_data.py

"""
WeatherData Entity for Cyoda Client Application

Stores weather information fetched from MSC GeoMet API for specific locations.
Represents weather data with temperature, humidity, wind speed, and conditions.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class WeatherData(CyodaEntity):
    """
    WeatherData entity represents weather information fetched from MSC GeoMet API.

    Stores weather data including temperature, humidity, wind speed, and conditions for specific locations.
    The state field manages workflow states: initial_state -> fetching -> processed -> notification_ready -> expired
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeatherData"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    subscription_id: str = Field(
        ..., description="Reference to WeatherSubscription (required)"
    )
    location: str = Field(..., description="Geographic location (required)")
    latitude: float = Field(..., description="Location latitude (required)")
    longitude: float = Field(..., description="Location longitude (required)")
    temperature: float = Field(..., description="Temperature in Celsius (required)")
    humidity: float = Field(..., description="Humidity percentage (required)")
    wind_speed: float = Field(..., description="Wind speed in km/h (required)")
    weather_condition: str = Field(
        ..., description="Weather description (e.g., 'Sunny', 'Cloudy') (required)"
    )
    fetch_timestamp: str = Field(
        ..., description="When data was fetched from API (required)"
    )
    forecast_date: str = Field(
        ..., description="Date for which weather is forecasted (required)"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the weather data was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the weather data was last updated (ISO 8601 format)",
    )

    @field_validator("subscription_id")
    @classmethod
    def validate_subscription_id(cls, v: str) -> str:
        """Validate subscription_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Subscription ID must be non-empty")

        if len(v) > 255:
            raise ValueError("Subscription ID must be at most 255 characters long")

        return v.strip()

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        """Validate location field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Location must be non-empty")

        if len(v) < 3:
            raise ValueError("Location must be at least 3 characters long")

        if len(v) > 255:
            raise ValueError("Location must be at most 255 characters long")

        return v.strip()

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude field (must be between -90 and 90)"""
        if v < -90.0 or v > 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees")

        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude field (must be between -180 and 180)"""
        if v < -180.0 or v > 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees")

        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature field (reasonable range in Celsius)"""
        if v < -100.0 or v > 100.0:
            raise ValueError("Temperature must be between -100 and 100 degrees Celsius")

        return v

    @field_validator("humidity")
    @classmethod
    def validate_humidity(cls, v: float) -> float:
        """Validate humidity field (percentage 0-100)"""
        if v < 0.0 or v > 100.0:
            raise ValueError("Humidity must be between 0 and 100 percent")

        return v

    @field_validator("wind_speed")
    @classmethod
    def validate_wind_speed(cls, v: float) -> float:
        """Validate wind_speed field (non-negative km/h)"""
        if v < 0.0:
            raise ValueError("Wind speed must be non-negative")

        if v > 500.0:  # Reasonable upper limit
            raise ValueError("Wind speed must be less than 500 km/h")

        return v

    @field_validator("weather_condition")
    @classmethod
    def validate_weather_condition(cls, v: str) -> str:
        """Validate weather_condition field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Weather condition must be non-empty")

        if len(v) > 100:
            raise ValueError("Weather condition must be at most 100 characters long")

        return v.strip()

    @field_validator("fetch_timestamp")
    @classmethod
    def validate_fetch_timestamp(cls, v: str) -> str:
        """Validate fetch_timestamp field (ISO 8601 format)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Fetch timestamp must be non-empty")

        # Try to parse the timestamp to validate format
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Fetch timestamp must be in ISO 8601 format")

        return v.strip()

    @field_validator("forecast_date")
    @classmethod
    def validate_forecast_date(cls, v: str) -> str:
        """Validate forecast_date field (YYYY-MM-DD format)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Forecast date must be non-empty")

        # Try to parse the date to validate format
        try:
            datetime.strptime(v.strip(), "%Y-%m-%d")
        except ValueError:
            raise ValueError("Forecast date must be in YYYY-MM-DD format")

        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "WeatherData":
        """Validate business logic rules"""
        # Business rule: Data expires after 24 hours
        # This is enforced at the application level through workflow transitions

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_expired(self) -> bool:
        """Check if weather data is expired (older than 24 hours)"""
        try:
            fetch_time = datetime.fromisoformat(
                self.fetch_timestamp.replace("Z", "+00:00")
            )
            current_time = datetime.now(timezone.utc)
            age_hours = (current_time - fetch_time).total_seconds() / 3600
            return age_hours > 24
        except (ValueError, AttributeError):
            return True  # Consider invalid timestamps as expired

    def get_coordinates(self) -> Dict[str, float]:
        """Get coordinates as a dictionary"""
        return {"latitude": self.latitude, "longitude": self.longitude}

    def get_summary(self) -> str:
        """Get a human-readable weather summary"""
        return (
            f"{self.weather_condition}, {self.temperature}°C, "
            f"{self.humidity}% humidity, wind {self.wind_speed} km/h"
        )

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
