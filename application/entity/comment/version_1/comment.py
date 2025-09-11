"""
Comment Entity for Cyoda Client Application

Represents a comment fetched from the JSONPlaceholder API.
Manages comment data and sentiment analysis results.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Comment(CyodaEntity):
    """
    Comment represents a comment fetched from the JSONPlaceholder API.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: fetched -> analyzed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Comment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements (matching API structure)
    id: int = Field(..., description="Unique identifier from JSONPlaceholder API")
    post_id: int = Field(
        ..., alias="postId", description="The post ID this comment belongs to"
    )
    name: str = Field(..., description="Comment title/name from API")
    email: str = Field(..., description="Email of the comment author")
    body: str = Field(..., description="Comment content/body")

    # Relationship fields
    analysis_request_id: int = Field(
        ...,
        alias="analysisRequestId",
        description="Foreign key to CommentAnalysisRequest",
    )

    # Analysis fields (populated during processing)
    sentiment: Optional[str] = Field(
        default=None, description="Analyzed sentiment (POSITIVE, NEGATIVE, NEUTRAL)"
    )
    word_count: Optional[int] = Field(
        default=None,
        alias="wordCount",
        description="Number of words in the comment body",
    )

    # Timestamps
    fetched_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="fetchedAt",
        description="Timestamp when the comment was fetched (ISO 8601 format)",
    )

    # Valid sentiment values
    VALID_SENTIMENTS: ClassVar[list[str]] = ["POSITIVE", "NEGATIVE", "NEUTRAL"]

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")

        # Basic email validation
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Email must be a valid email format")

        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        """Validate body is not null or empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Comment body must be non-empty")
        return v.strip()

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: Optional[str]) -> Optional[str]:
        """Validate sentiment is one of the allowed values"""
        if v is not None and v not in cls.VALID_SENTIMENTS:
            raise ValueError(f"Sentiment must be one of: {cls.VALID_SENTIMENTS}")
        return v

    @field_validator("word_count")
    @classmethod
    def validate_word_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate word count is positive"""
        if v is not None and v < 0:
            raise ValueError("Word count must be non-negative")
        return v

    def count_words(self) -> int:
        """Count words in the comment body"""
        if not self.body:
            return 0
        # Simple word counting - split by whitespace
        words = self.body.strip().split()
        return len(words)

    def set_word_count(self) -> None:
        """Set word count based on body content"""
        self.word_count = self.count_words()
        self.update_timestamp()

    def set_sentiment(self, sentiment: str) -> None:
        """Set sentiment analysis result"""
        if sentiment not in self.VALID_SENTIMENTS:
            raise ValueError(f"Sentiment must be one of: {self.VALID_SENTIMENTS}")
        self.sentiment = sentiment
        self.update_timestamp()

    def is_analyzed(self) -> bool:
        """Check if comment has been analyzed (has sentiment)"""
        return self.sentiment is not None

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
