# entity/analysis/version_1/analysis.py

"""
Analysis Entity for Cyoda Client Application

Represents the results of comment analysis including sentiment, keywords, and metrics.
Stores analysis data for comments as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Analysis(CyodaEntity):
    """
    Analysis entity represents the results of comment analysis.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> processing -> completed/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Analysis"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    comment_id: str = Field(..., description="Reference to the analyzed comment")

    # Analysis result fields (populated during processing)
    sentiment_score: Optional[float] = Field(
        default=None, description="Numerical sentiment analysis result (-1 to 1)"
    )
    sentiment_label: Optional[str] = Field(
        default=None, description="Text label (positive, negative, neutral)"
    )
    keywords: Optional[List[str]] = Field(
        default=None, description="Extracted keywords from the comment"
    )
    language: Optional[str] = Field(
        default=None, description="Detected language of the comment"
    )
    toxicity_score: Optional[float] = Field(
        default=None, description="Content toxicity assessment (0 to 1)"
    )
    analyzed_at: Optional[str] = Field(
        default=None, description="When the analysis was performed (ISO 8601 format)"
    )

    # Processing status fields
    status: Optional[str] = Field(
        default=None,
        description="Processing status (processing, completed, failed, retrying)",
    )
    retry_count: Optional[int] = Field(
        default=0, description="Number of retry attempts"
    )
    last_retry_at: Optional[str] = Field(
        default=None, description="When the last retry was attempted (ISO 8601 format)"
    )
    completed_at: Optional[str] = Field(
        default=None, description="When the analysis was completed (ISO 8601 format)"
    )

    # Allowed sentiment labels
    ALLOWED_SENTIMENT_LABELS: ClassVar[List[str]] = ["positive", "negative", "neutral"]

    @field_validator("comment_id")
    @classmethod
    def validate_comment_id(cls, v: str) -> str:
        """Validate comment_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Comment ID must be non-empty")
        return v.strip()

    @field_validator("sentiment_score")
    @classmethod
    def validate_sentiment_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate sentiment_score field (must be between -1 and 1)"""
        if v is not None:
            if v < -1.0 or v > 1.0:
                raise ValueError("Sentiment score must be between -1 and 1")
        return v

    @field_validator("sentiment_label")
    @classmethod
    def validate_sentiment_label(cls, v: Optional[str]) -> Optional[str]:
        """Validate sentiment_label field"""
        if v is not None:
            if v not in cls.ALLOWED_SENTIMENT_LABELS:
                raise ValueError(
                    f"Sentiment label must be one of: {cls.ALLOWED_SENTIMENT_LABELS}"
                )
        return v

    @field_validator("toxicity_score")
    @classmethod
    def validate_toxicity_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate toxicity_score field (must be between 0 and 1)"""
        if v is not None:
            if v < 0.0 or v > 1.0:
                raise ValueError("Toxicity score must be between 0 and 1")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language field"""
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Language must be non-empty if provided")
            if len(v) > 10:
                raise ValueError("Language code must be at most 10 characters long")
            return v.strip()
        return v

    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate retry_count field"""
        if v is not None and v < 0:
            raise ValueError("Retry count must be non-negative")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Analysis":
        """Validate business logic rules"""
        # Ensure keywords is a list if provided
        if self.keywords is not None and not isinstance(self.keywords, list):
            raise ValueError("Keywords must be a list")

        # Validate that if sentiment_score is provided, sentiment_label should also be provided
        if self.sentiment_score is not None and self.sentiment_label is None:
            # Auto-determine sentiment label based on score
            if self.sentiment_score > 0.1:
                self.sentiment_label = "positive"
            elif self.sentiment_score < -0.1:
                self.sentiment_label = "negative"
            else:
                self.sentiment_label = "neutral"

        return self

    def set_analyzed_at(self) -> None:
        """Set the analyzed_at timestamp to current time"""
        self.analyzed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_completed_at(self) -> None:
        """Set the completed_at timestamp to current time"""
        self.completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def set_last_retry_at(self) -> None:
        """Set the last_retry_at timestamp to current time"""
        self.last_retry_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def increment_retry_count(self) -> None:
        """Increment retry count and update timestamp"""
        if self.retry_count is None:
            self.retry_count = 0
        self.retry_count += 1
        self.set_last_retry_at()
        self.update_timestamp()

    def set_analysis_results(
        self,
        sentiment_score: float,
        sentiment_label: str,
        keywords: List[str],
        language: str,
        toxicity_score: float,
    ) -> None:
        """Set all analysis results and update timestamp"""
        self.sentiment_score = sentiment_score
        self.sentiment_label = sentiment_label
        self.keywords = keywords
        self.language = language
        self.toxicity_score = toxicity_score
        self.set_analyzed_at()
        self.update_timestamp()

    def is_processing(self) -> bool:
        """Check if analysis is currently processing"""
        return self.state == "processing"

    def is_completed(self) -> bool:
        """Check if analysis has been completed"""
        return self.state == "completed"

    def is_failed(self) -> bool:
        """Check if analysis has failed"""
        return self.state == "failed"

    def has_all_results(self) -> bool:
        """Check if all analysis results are present"""
        return (
            self.sentiment_score is not None
            and self.sentiment_label is not None
            and self.keywords is not None
            and self.language is not None
            and self.toxicity_score is not None
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
