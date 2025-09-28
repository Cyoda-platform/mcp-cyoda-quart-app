# entity/comment/version_1/comment.py

"""
Comment Entity for Cyoda Client Application

Represents individual comments fetched from JSONPlaceholder API
with analysis results and processing status.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Comment(CyodaEntity):
    """
    Comment entity represents individual comments from JSONPlaceholder API
    with analysis results and processing metadata.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> ingested -> analyzed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Comment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Original comment data from JSONPlaceholder API
    post_id: int = Field(
        ..., alias="postId", description="ID of the post this comment belongs to"
    )
    comment_id: int = Field(
        ..., alias="commentId", description="Original comment ID from API"
    )
    name: str = Field(..., description="Comment title/name from API")
    email: str = Field(..., description="Email address of the commenter")
    body: str = Field(..., description="Comment body text")

    # Analysis results (populated during processing)
    sentiment_score: Optional[float] = Field(
        default=None,
        alias="sentimentScore",
        description="Sentiment analysis score (-1.0 to 1.0, negative to positive)",
    )
    sentiment_label: Optional[str] = Field(
        default=None,
        alias="sentimentLabel",
        description="Sentiment classification: POSITIVE, NEGATIVE, NEUTRAL",
    )
    word_count: Optional[int] = Field(
        default=None,
        alias="wordCount",
        description="Number of words in the comment body",
    )
    contains_keywords: Optional[List[str]] = Field(
        default=None,
        alias="containsKeywords",
        description="List of detected keywords in the comment",
    )

    # Processing metadata
    analyzed_at: Optional[str] = Field(
        default=None,
        alias="analyzedAt",
        description="Timestamp when analysis was completed (ISO 8601 format)",
    )
    analysis_version: Optional[str] = Field(
        default=None,
        alias="analysisVersion",
        description="Version of analysis algorithm used",
    )

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the comment was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the comment was last updated (ISO 8601 format)",
    )

    # Validation constants
    VALID_SENTIMENT_LABELS: ClassVar[List[str]] = ["POSITIVE", "NEGATIVE", "NEUTRAL"]

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation"""
        if not v or "@" not in v:
            raise ValueError("Email must contain @ symbol")
        return v.strip().lower()

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        """Validate comment body"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Comment body cannot be empty")
        if len(v) > 5000:
            raise ValueError("Comment body too long (max 5000 characters)")
        return v.strip()

    @field_validator("sentiment_label")
    @classmethod
    def validate_sentiment_label(cls, v: Optional[str]) -> Optional[str]:
        """Validate sentiment label if provided"""
        if v is not None and v not in cls.VALID_SENTIMENT_LABELS:
            raise ValueError(
                f"Sentiment label must be one of: {cls.VALID_SENTIMENT_LABELS}"
            )
        return v

    @field_validator("sentiment_score")
    @classmethod
    def validate_sentiment_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate sentiment score range"""
        if v is not None and (v < -1.0 or v > 1.0):
            raise ValueError("Sentiment score must be between -1.0 and 1.0")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_analysis_results(
        self,
        sentiment_score: float,
        sentiment_label: str,
        word_count: int,
        keywords: List[str],
        analysis_version: str = "1.0",
    ) -> None:
        """Set analysis results and update timestamps"""
        self.sentiment_score = sentiment_score
        self.sentiment_label = sentiment_label
        self.word_count = word_count
        self.contains_keywords = keywords
        self.analysis_version = analysis_version
        self.analyzed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_analyzed(self) -> bool:
        """Check if comment has been analyzed"""
        return self.sentiment_score is not None and self.sentiment_label is not None

    def get_business_id(self) -> str:
        """Get business identifier for this comment"""
        return f"post_{self.post_id}_comment_{self.comment_id}"

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
