# entity/weathersubscription/version_1/weather_subscription.py

"""
WeatherSubscription Entity for Cyoda Client Application

Manages user subscriptions to weather updates for specific locations.
Represents location-based weather subscriptions with coordinates and frequency settings.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class WeatherSubscription(CyodaEntity):
    """
    WeatherSubscription entity represents a user's subscription to weather updates for a specific location.
    
    Manages location-based subscriptions with coordinates, frequency, and active status.
    The state field manages workflow states: initial_state -> created -> active -> paused/cancelled
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "WeatherSubscription"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    user_id: str = Field(..., description="Reference to User entity (required)")
    location: str = Field(
        ..., description="Geographic location (city, province/state, country) (required)"
    )
    latitude: float = Field(
        ..., description="Location latitude for API calls (required)"
    )
    longitude: float = Field(
        ..., description="Location longitude for API calls (required)"
    )
    frequency: str = Field(
        default="daily", description="Notification frequency (daily, weekly)"
    )
    active: bool = Field(
        default=True, description="Whether subscription is active"
    )

    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the subscription was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the subscription was last updated (ISO 8601 format)",
    )

    # Allowed frequency values
    ALLOWED_FREQUENCIES: ClassVar[List[str]] = ["daily", "weekly"]

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID must be non-empty")
        
        if len(v) > 255:
            raise ValueError("User ID must be at most 255 characters long")
        
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

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate frequency field"""
        if not v or len(v.strip()) == 0:
            return "daily"
        
        v_clean = v.strip().lower()
        if v_clean not in cls.ALLOWED_FREQUENCIES:
            raise ValueError(f"Frequency must be one of: {cls.ALLOWED_FREQUENCIES}")
        
        return v_clean

    @model_validator(mode="after")
    def validate_business_logic(self) -> "WeatherSubscription":
        """Validate business logic rules"""
        # Business rule: Location coordinates must be valid
        # This is already handled by individual field validators
        
        # Business rule: Only active subscriptions generate notifications
        # This is enforced at the application level
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def deactivate(self) -> None:
        """Deactivate subscription"""
        self.active = False
        self.update_timestamp()

    def activate(self) -> None:
        """Activate subscription"""
        self.active = True
        self.update_timestamp()

    def pause(self) -> None:
        """Pause subscription (alias for deactivate)"""
        self.deactivate()

    def resume(self) -> None:
        """Resume subscription (alias for activate)"""
        self.activate()

    def is_notification_eligible(self) -> bool:
        """Check if subscription is eligible to generate notifications"""
        return self.active and self.state in ["active"]

    def get_coordinates(self) -> Dict[str, float]:
        """Get coordinates as a dictionary"""
        return {"latitude": self.latitude, "longitude": self.longitude}

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
