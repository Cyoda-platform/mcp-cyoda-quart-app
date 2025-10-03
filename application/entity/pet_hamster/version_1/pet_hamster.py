# entity/pet_hamster/version_1/pet_hamster.py

"""
PetHamster Entity for Cyoda Client Application

Represents a pet hamster that can be safely approached and petted through
a controlled workflow with mood analysis, safety checks, and interaction logging.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class PetHamster(CyodaEntity):
    """
    PetHamster represents a pet hamster entity that goes through a workflow
    for safe approaching and petting with mood analysis and safety checks.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: INITIAL -> APPROACH -> CHECK_MOOD -> PICK_UP -> PET -> FINISH
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "PetHamster"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Name of the pet hamster")
    breed: Optional[str] = Field(
        default=None, description="Breed of the hamster (e.g., Syrian, Dwarf)"
    )
    age_months: Optional[int] = Field(
        default=None,
        alias="ageMonths",
        description="Age of the hamster in months",
    )

    # Mood and behavior fields (populated by camera analysis)
    mood: Optional[str] = Field(
        default=None,
        description="Current mood of the hamster (calm, agitated, sleeping, etc.)",
    )
    activity_level: Optional[str] = Field(
        default=None,
        alias="activityLevel",
        description="Current activity level (low, medium, high)",
    )

    # Safety and handling fields
    is_safe_to_handle: Optional[bool] = Field(
        default=None,
        alias="isSafeToHandle",
        description="Flag indicating if the hamster is safe to handle",
    )
    last_handled_at: Optional[str] = Field(
        default=None,
        alias="lastHandledAt",
        description="Timestamp when the hamster was last handled (ISO 8601 format)",
    )

    # Location and environment
    current_location: Optional[str] = Field(
        default="cage",
        alias="currentLocation",
        description="Current location of the hamster (cage, hand, play_area)",
    )

    # Interaction history and logging
    interaction_count: Optional[int] = Field(
        default=0,
        alias="interactionCount",
        description="Total number of successful interactions",
    )
    last_interaction_result: Optional[str] = Field(
        default=None,
        alias="lastInteractionResult",
        description="Result of the last interaction (success, bite, escape, etc.)",
    )

    # Processing data from workflow processors
    camera_analysis_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="cameraAnalysisData",
        description="Data from camera analysis processor",
    )
    safety_check_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="safetyCheckData",
        description="Data from safety check processor",
    )
    interaction_log_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="interactionLogData",
        description="Data from interaction logger processor",
    )

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the entity was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the entity was last updated (ISO 8601 format)",
    )

    # Validation constants
    ALLOWED_MOODS: ClassVar[List[str]] = [
        "calm",
        "agitated",
        "sleeping",
        "eating",
        "playing",
        "hiding",
        "curious",
    ]

    ALLOWED_LOCATIONS: ClassVar[List[str]] = [
        "cage",
        "hand",
        "play_area",
        "unknown",
    ]

    ALLOWED_ACTIVITY_LEVELS: ClassVar[List[str]] = [
        "low",
        "medium",
        "high",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Name must be at most 50 characters long")
        return v.strip()

    @field_validator("age_months")
    @classmethod
    def validate_age_months(cls, v: Optional[int]) -> Optional[int]:
        """Validate age in months"""
        if v is not None:
            if v < 0:
                raise ValueError("Age must be non-negative")
            if v > 60:  # Hamsters typically live 2-5 years
                raise ValueError("Age must be realistic for a hamster (max 60 months)")
        return v

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, v: Optional[str]) -> Optional[str]:
        """Validate mood field"""
        if v is not None and v not in cls.ALLOWED_MOODS:
            raise ValueError(f"Mood must be one of: {cls.ALLOWED_MOODS}")
        return v

    @field_validator("current_location")
    @classmethod
    def validate_current_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate current location field"""
        if v is not None and v not in cls.ALLOWED_LOCATIONS:
            raise ValueError(
                f"Current location must be one of: {cls.ALLOWED_LOCATIONS}"
            )
        return v

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate activity level field"""
        if v is not None and v not in cls.ALLOWED_ACTIVITY_LEVELS:
            raise ValueError(
                f"Activity level must be one of: {cls.ALLOWED_ACTIVITY_LEVELS}"
            )
        return v

    @field_validator("interaction_count")
    @classmethod
    def validate_interaction_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate interaction count"""
        if v is not None and v < 0:
            raise ValueError("Interaction count must be non-negative")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_camera_analysis_data(self, analysis_data: Dict[str, Any]) -> None:
        """Set camera analysis data and update timestamp"""
        self.camera_analysis_data = analysis_data
        self.update_timestamp()

    def set_safety_check_data(self, safety_data: Dict[str, Any]) -> None:
        """Set safety check data and update timestamp"""
        self.safety_check_data = safety_data
        self.update_timestamp()

    def set_interaction_log_data(self, log_data: Dict[str, Any]) -> None:
        """Set interaction log data and update timestamp"""
        self.interaction_log_data = log_data
        self.update_timestamp()

    def is_calm(self) -> bool:
        """Check if hamster is in a calm mood"""
        return self.mood == "calm"

    def is_safe_for_interaction(self) -> bool:
        """Check if hamster is safe for interaction"""
        return self.is_safe_to_handle is True and self.mood == "calm"

    def increment_interaction_count(self) -> None:
        """Increment the interaction count"""
        if self.interaction_count is None:
            self.interaction_count = 1
        else:
            self.interaction_count += 1
        self.update_timestamp()

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
