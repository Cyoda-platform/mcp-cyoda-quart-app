# entity/catfact/version_1/catfact.py

"""
CatFact Entity for Cyoda Client Application

Represents a cat fact retrieved from the external API and stored for weekly distribution.
Manages the lifecycle from retrieval to archival.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CatFact(CyodaEntity):
    """
    CatFact represents a cat fact retrieved from the external API and stored for weekly distribution.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> retrieved -> scheduled -> sent -> archived -> end
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CatFact"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    fact_text: str = Field(
        ..., alias="factText", description="The actual cat fact content (required)"
    )
    fact_length: int = Field(
        ..., alias="factLength", description="Length of the fact text"
    )
    retrieved_date: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="retrievedDate",
        description="Date and time when the fact was retrieved from API (ISO 8601 format)",
    )
    scheduled_send_date: Optional[str] = Field(
        default=None,
        alias="scheduledSendDate",
        description="Date when this fact is scheduled to be sent (ISO 8601 date format)",
    )
    external_fact_id: Optional[str] = Field(
        default=None,
        alias="externalFactId",
        description="Original ID from the Cat Fact API (if available)",
    )

    @field_validator("fact_text")
    @classmethod
    def validate_fact_text(cls, v: str) -> str:
        """Validate fact text field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Cat fact text cannot be empty")

        v = v.strip()
        if len(v) < 10:
            raise ValueError("Cat fact text must be at least 10 characters long")

        if len(v) > 500:
            raise ValueError("Cat fact text must be at most 500 characters long")

        return v

    @field_validator("fact_length", mode="before")
    @classmethod
    def calculate_fact_length(cls, v: Any, info: Any) -> int:
        """Calculate fact length from fact_text if not provided"""
        if v is not None:
            return v

        # Get fact_text from the values being validated
        fact_text = info.data.get("fact_text") or info.data.get("factText")
        if fact_text:
            return len(fact_text.strip())

        return 0

    @field_validator("fact_length")
    @classmethod
    def validate_fact_length(cls, v: int) -> int:
        """Validate fact length field"""
        if v < 10:
            raise ValueError("Cat fact length must be at least 10 characters")

        if v > 500:
            raise ValueError("Cat fact length must be at most 500 characters")

        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def schedule_for_date(self, send_date: str) -> None:
        """Schedule the cat fact for a specific send date"""
        self.scheduled_send_date = send_date
        self.update_timestamp()

    def is_ready_for_scheduling(self) -> bool:
        """Check if cat fact is ready for scheduling (in retrieved state)"""
        return self.state == "retrieved"

    def is_scheduled(self) -> bool:
        """Check if cat fact is scheduled for sending"""
        return self.state == "scheduled" and self.scheduled_send_date is not None

    def is_sent(self) -> bool:
        """Check if cat fact has been sent"""
        return self.state == "sent"

    def is_archived(self) -> bool:
        """Check if cat fact has been archived"""
        return self.state == "archived"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["id"] = self.get_id()
        data["state"] = self.state
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
