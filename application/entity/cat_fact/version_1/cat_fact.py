# entity/cat_fact/version_1/cat_fact.py

"""
CatFact Entity for Cat Fact Subscription Application

Represents cat facts retrieved from external APIs.
Manages fact content, source information, and usage tracking.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CatFact(CyodaEntity):
    """
    CatFact represents a cat fact retrieved from an external API.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> retrieved -> validated -> ready_for_use
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CatFact"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    fact_text: str = Field(..., alias="factText", description="The cat fact content")
    source: str = Field(default="catfact.ninja", description="Source of the cat fact")
    
    # API-related fields
    api_id: Optional[str] = Field(
        default=None,
        alias="apiId",
        description="ID from the external API (if available)"
    )
    api_length: Optional[int] = Field(
        default=None,
        alias="apiLength", 
        description="Length of the fact as reported by API"
    )
    
    # Timestamps
    retrieved_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="retrievedAt",
        description="Timestamp when the fact was retrieved (ISO 8601 format)"
    )
    
    # Usage tracking
    is_used: bool = Field(
        default=False,
        alias="isUsed",
        description="Whether this fact has been used in an email campaign"
    )
    used_in_campaign_id: Optional[str] = Field(
        default=None,
        alias="usedInCampaignId",
        description="ID of the email campaign where this fact was used"
    )
    used_at: Optional[str] = Field(
        default=None,
        alias="usedAt",
        description="Timestamp when the fact was used in a campaign"
    )
    
    # Quality and validation
    quality_score: Optional[float] = Field(
        default=None,
        alias="qualityScore",
        description="Quality score of the fact (0.0 to 1.0)"
    )
    is_appropriate: bool = Field(
        default=True,
        alias="isAppropriate",
        description="Whether the fact is appropriate for email distribution"
    )
    validation_notes: Optional[str] = Field(
        default=None,
        alias="validationNotes",
        description="Notes from validation process"
    )

    @field_validator("fact_text")
    @classmethod
    def validate_fact_text(cls, v: str) -> str:
        """Validate fact text field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Fact text must be non-empty")
        
        if len(v) < 10:
            raise ValueError("Fact text must be at least 10 characters long")
            
        if len(v) > 1000:
            raise ValueError("Fact text must be at most 1000 characters long")
            
        return v.strip()

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Source must be non-empty")
            
        if len(v) > 100:
            raise ValueError("Source must be at most 100 characters long")
            
        return v.strip()

    @field_validator("quality_score")
    @classmethod
    def validate_quality_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate quality score is between 0.0 and 1.0"""
        if v is None:
            return v
            
        if not (0.0 <= v <= 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")
            
        return v

    def mark_as_used(self, campaign_id: str) -> None:
        """Mark this fact as used in a campaign"""
        self.is_used = True
        self.used_in_campaign_id = campaign_id
        self.used_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_quality_score(self, score: float, notes: Optional[str] = None) -> None:
        """Set quality score and validation notes"""
        if not (0.0 <= score <= 1.0):
            raise ValueError("Quality score must be between 0.0 and 1.0")
            
        self.quality_score = score
        if notes:
            self.validation_notes = notes

    def mark_inappropriate(self, reason: str) -> None:
        """Mark fact as inappropriate with reason"""
        self.is_appropriate = False
        self.validation_notes = f"Marked inappropriate: {reason}"

    def is_available_for_use(self) -> bool:
        """Check if fact is available for use in campaigns"""
        return (
            not self.is_used 
            and self.is_appropriate 
            and self.state in ["validated", "ready_for_use"]
        )

    def get_word_count(self) -> int:
        """Get word count of the fact text"""
        return len(self.fact_text.split())

    def get_character_count(self) -> int:
        """Get character count of the fact text"""
        return len(self.fact_text)

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["wordCount"] = self.get_word_count()
        data["characterCount"] = self.get_character_count()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
