# entity/cat_fact/version_1/cat_fact.py

"""
CatFact Entity for Cat Fact Subscription Application

Represents a cat fact retrieved from the Cat Fact API that can be sent to subscribers.
Manages fact content, source information, and delivery tracking.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CatFact(CyodaEntity):
    """
    CatFact entity represents a cat fact retrieved from an external API.

    Manages fact content, source information, and delivery tracking.
    The state field manages workflow states: initial_state -> ingested -> validated -> ready_for_delivery
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CatFact"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    fact: str = Field(..., description="The cat fact content")

    # Source information
    source_api: str = Field(
        default="catfact.ninja",
        alias="sourceApi",
        description="API source of the cat fact",
    )
    source_id: Optional[str] = Field(
        default=None, alias="sourceId", description="Original ID from the source API"
    )

    # Content metadata
    fact_length: Optional[int] = Field(
        default=None, alias="factLength", description="Length of the fact in characters"
    )

    # Timestamps
    ingested_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="ingestedAt",
        description="Timestamp when the fact was ingested (ISO 8601 format)",
    )

    # Delivery tracking
    is_used_for_delivery: bool = Field(
        default=False,
        alias="isUsedForDelivery",
        description="Whether this fact has been used in an email campaign",
    )
    delivery_date: Optional[str] = Field(
        default=None,
        alias="deliveryDate",
        description="Date when this fact was delivered to subscribers",
    )
    campaign_id: Optional[str] = Field(
        default=None,
        alias="campaignId",
        description="ID of the email campaign that used this fact",
    )

    # Quality metrics
    quality_score: Optional[float] = Field(
        default=None,
        alias="qualityScore",
        description="Quality score of the fact (0.0 to 1.0)",
    )
    is_appropriate: bool = Field(
        default=True,
        alias="isAppropriate",
        description="Whether the fact is appropriate for email delivery",
    )

    @field_validator("fact")
    @classmethod
    def validate_fact(cls, v: str) -> str:
        """Validate fact content"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Fact content must be non-empty")

        if len(v) < 10:
            raise ValueError("Fact must be at least 10 characters long")

        if len(v) > 1000:
            raise ValueError("Fact must be at most 1000 characters long")

        return v.strip()

    @field_validator("quality_score")
    @classmethod
    def validate_quality_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate quality score"""
        if v is None:
            return v

        if not 0.0 <= v <= 1.0:
            raise ValueError("Quality score must be between 0.0 and 1.0")

        return v

    def calculate_fact_length(self) -> None:
        """Calculate and set the fact length"""
        self.fact_length = len(self.fact)

    def mark_as_delivered(self, campaign_id: str) -> None:
        """Mark this fact as delivered in a campaign"""
        self.is_used_for_delivery = True
        self.delivery_date = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.campaign_id = campaign_id

    def set_quality_score(self, score: float) -> None:
        """Set the quality score for this fact"""
        if not 0.0 <= score <= 1.0:
            raise ValueError("Quality score must be between 0.0 and 1.0")
        self.quality_score = score

    def mark_inappropriate(self) -> None:
        """Mark this fact as inappropriate for delivery"""
        self.is_appropriate = False

    def is_ready_for_delivery(self) -> bool:
        """Check if this fact is ready for delivery"""
        return (
            self.is_appropriate
            and not self.is_used_for_delivery
            and self.state == "ready_for_delivery"
        )

    def get_preview(self, max_length: int = 100) -> str:
        """Get a preview of the fact content"""
        if len(self.fact) <= max_length:
            return self.fact
        return self.fact[: max_length - 3] + "..."

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
