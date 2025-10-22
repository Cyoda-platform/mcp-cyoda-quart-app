"""
Pet entity for Cyoda Client Application

Represents a pet ingested from the pet store API with workflow capabilities
for processing and validation.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents a pet from the pet store API.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> ingested -> validated -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from pet store API
    name: str = Field(..., description="Name of the pet")
    pet_type: str = Field(..., alias="petType", description="Type of pet (e.g., dog, cat)")
    status: Optional[str] = Field(
        default="available",
        description="Status of the pet (available, pending, sold)",
    )

    # Optional fields from pet store API
    photo_urls: Optional[List[str]] = Field(
        default=None,
        alias="photoUrls",
        description="List of photo URLs for the pet",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags associated with the pet",
    )
    price: Optional[float] = Field(
        default=None,
        description="Price of the pet",
    )

    # Processing fields
    ingestion_timestamp: Optional[str] = Field(
        default=None,
        alias="ingestionTimestamp",
        description="Timestamp when the pet was ingested from the API",
    )
    processing_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processingResult",
        description="Result of processing the pet data",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        if len(v) > 100:
            raise ValueError("Name must be at most 100 characters long")
        return v.strip()

    @field_validator("pet_type")
    @classmethod
    def validate_pet_type(cls, v: str) -> str:
        """Validate pet type field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet type must be non-empty")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status field"""
        if v is not None:
            allowed_statuses = ["available", "pending", "sold"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    def update_ingestion_timestamp(self) -> None:
        """Update the ingestion timestamp to current time"""
        self.ingestion_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_processing_result(self, result: Dict[str, Any]) -> None:
        """Set processing result"""
        self.processing_result = result

    def is_ready_for_processing(self) -> bool:
        """Check if pet is ready for processing"""
        return self.state == "validated"

    def is_processed(self) -> bool:
        """Check if pet has been processed"""
        return self.state in ["processed", "completed"]

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )

