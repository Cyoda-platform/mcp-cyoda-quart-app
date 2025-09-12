# entity/example_entity/version_1/example_entity.py

"""
ExampleEntity for Cyoda Client Application

Represents the primary business object that demonstrates core workflow functionality
with processing and validation capabilities as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class ExampleEntity(CyodaEntity):
    """
    ExampleEntity represents a primary business object that demonstrates
    the core workflow functionality with processing and validation capabilities.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> created -> validated -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "ExampleEntity"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Name of the example entity")
    description: str = Field(..., description="Description of the entity")
    value: float = Field(..., description="Numeric value for the entity")
    category: str = Field(..., description="Category classification for the entity")
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Flag indicating if the entity is active"
    )

    # Timestamps (inherited created_at from CyodaEntity, but need to override updated_at behavior)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the entity was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the entity was last updated (ISO 8601 format)",
    )

    # Processing-related fields (populated during processing)
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data that gets populated during processing",
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="validationResult",
        description="Result of validation checks",
    )

    # Validation rules from criteria requirements
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "ELECTRONICS",
        "CLOTHING",
        "BOOKS",
        "HOME",
        "SPORTS",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        if len(v) < 3:
            raise ValueError("Name must be at least 3 characters long")
        if len(v) > 100:
            raise ValueError("Name must be at most 100 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 500:
            raise ValueError("Description must be at most 500 characters long")
        return v.strip()

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        """Validate value field according to criteria requirements"""
        if v < 0:
            raise ValueError("Value must be non-negative")
        if v > 10000:
            raise ValueError("Value must be at most 10000")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category field according to criteria requirements"""
        if v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "ExampleEntity":
        """Validate business logic rules according to criteria requirements"""
        category = self.category
        is_active = self.is_active

        # Simplified business logic without numeric value constraints
        if category not in self.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {self.ALLOWED_CATEGORIES}")

        if is_active is False and category == "ELECTRONICS":
            raise ValueError("ELECTRONICS category entities must be active")

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def set_validation_result(self, validation_result: Dict[str, Any]) -> None:
        """Set validation result and update timestamp"""
        self.validation_result = validation_result
        self.update_timestamp()

    def is_ready_for_processing(self) -> bool:
        """Check if entity is ready for processing (in validated state)"""
        return self.state == "validated"

    def is_processed(self) -> bool:
        """Check if entity has been processed"""
        return self.state == "processed" or self.state == "completed"

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
