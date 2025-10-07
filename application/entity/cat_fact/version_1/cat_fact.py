# entity/cat_fact/version_1/cat_fact.py

"""
CatFact Entity for Cat Facts Subscription System

Represents a cat fact retrieved from external APIs and stored for distribution
to subscribers. Manages fact content, source information, and usage tracking.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CatFact(CyodaEntity):
    """
    CatFact entity represents a cat fact retrieved from external sources.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> retrieved -> validated -> ready -> sent
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CatFact"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    fact_text: str = Field(..., description="The cat fact content")
    source_api: str = Field(..., description="API source where fact was retrieved from")
    
    # Optional fields
    fact_id: Optional[str] = Field(
        default=None,
        description="Original ID from the source API"
    )
    category: Optional[str] = Field(
        default="general",
        description="Category of the cat fact"
    )
    
    # Retrieval metadata
    retrieved_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when fact was retrieved (ISO 8601 format)"
    )
    api_response_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Original API response data for reference"
    )
    
    # Quality and validation
    fact_length: int = Field(
        default=0,
        description="Length of the fact text in characters"
    )
    is_validated: bool = Field(
        default=False,
        description="Whether the fact has been validated for quality"
    )
    validation_score: Optional[float] = Field(
        default=None,
        description="Quality validation score (0.0 to 1.0)"
    )
    
    # Usage tracking
    times_sent: int = Field(
        default=0,
        description="Number of times this fact has been sent to subscribers"
    )
    last_sent_at: Optional[str] = Field(
        default=None,
        description="Timestamp when fact was last sent (ISO 8601 format)"
    )
    
    # Email campaign tracking
    campaign_ids: list[str] = Field(
        default_factory=list,
        description="List of email campaign IDs that used this fact"
    )
    
    # Validation constants
    ALLOWED_SOURCES: ClassVar[list[str]] = [
        "catfact.ninja",
        "cat-facts-api",
        "meowfacts",
        "manual_entry",
        "other"
    ]
    
    ALLOWED_CATEGORIES: ClassVar[list[str]] = [
        "general",
        "behavior",
        "health",
        "history",
        "breeds",
        "fun",
        "science"
    ]

    @field_validator("fact_text")
    @classmethod
    def validate_fact_text(cls, v: str) -> str:
        """Validate fact text field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Fact text must be non-empty")
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Fact text must be at least 10 characters long")
        if len(v) > 1000:
            raise ValueError("Fact text must be at most 1000 characters long")
        return v

    @field_validator("source_api")
    @classmethod
    def validate_source_api(cls, v: str) -> str:
        """Validate source API field"""
        if v not in cls.ALLOWED_SOURCES:
            raise ValueError(f"Source API must be one of: {cls.ALLOWED_SOURCES}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category field"""
        if v is not None and v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v

    @field_validator("validation_score")
    @classmethod
    def validate_validation_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate validation score field"""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Validation score must be between 0.0 and 1.0")
        return v

    def __init__(self, **data: Any) -> None:
        """Initialize CatFact and calculate fact length"""
        super().__init__(**data)
        if self.fact_text:
            self.fact_length = len(self.fact_text)

    def validate_fact(self, score: float) -> None:
        """Mark fact as validated with a quality score"""
        if score < 0.0 or score > 1.0:
            raise ValueError("Validation score must be between 0.0 and 1.0")
        self.is_validated = True
        self.validation_score = score
        self.update_timestamp()

    def mark_as_sent(self, campaign_id: str) -> None:
        """Record that this fact was sent in an email campaign"""
        self.times_sent += 1
        self.last_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if campaign_id not in self.campaign_ids:
            self.campaign_ids.append(campaign_id)
        self.update_timestamp()

    def is_ready_for_sending(self) -> bool:
        """Check if fact is ready to be sent to subscribers"""
        return (
            self.is_validated and 
            self.validation_score is not None and 
            self.validation_score >= 0.7 and
            len(self.fact_text.strip()) >= 10
        )

    def get_usage_frequency(self) -> str:
        """Get usage frequency category"""
        if self.times_sent == 0:
            return "unused"
        elif self.times_sent == 1:
            return "used_once"
        elif self.times_sent <= 3:
            return "low_usage"
        elif self.times_sent <= 10:
            return "medium_usage"
        else:
            return "high_usage"

    def get_age_in_days(self) -> int:
        """Get age of the fact in days since retrieval"""
        if not self.retrieved_at:
            return 0
        
        retrieved_dt = datetime.fromisoformat(self.retrieved_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - retrieved_dt).days

    def is_fresh(self, max_age_days: int = 30) -> bool:
        """Check if fact is fresh (not too old)"""
        return self.get_age_in_days() <= max_age_days

    def get_quality_rating(self) -> str:
        """Get quality rating based on validation score"""
        if not self.is_validated or self.validation_score is None:
            return "unvalidated"
        elif self.validation_score >= 0.9:
            return "excellent"
        elif self.validation_score >= 0.8:
            return "good"
        elif self.validation_score >= 0.7:
            return "acceptable"
        else:
            return "poor"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["usage_frequency"] = self.get_usage_frequency()
        data["age_in_days"] = self.get_age_in_days()
        data["is_fresh"] = self.is_fresh()
        data["quality_rating"] = self.get_quality_rating()
        data["is_ready_for_sending"] = self.is_ready_for_sending()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
