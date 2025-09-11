"""
CommentAnalysisReport Entity for Cyoda Client Application

Represents the analysis report generated from comments.
Contains aggregated statistics and report content for email delivery.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CommentAnalysisReport(CyodaEntity):
    """
    CommentAnalysisReport represents the analysis report generated from comments.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: generated -> sent -> complete
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CommentAnalysisReport"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    analysis_request_id: int = Field(
        ...,
        alias="analysisRequestId",
        description="Foreign key to CommentAnalysisRequest",
    )

    # Analysis statistics
    total_comments: int = Field(
        ..., alias="totalComments", description="Total number of comments analyzed"
    )
    positive_comments: int = Field(
        ...,
        alias="positiveComments",
        description="Number of positive sentiment comments",
    )
    negative_comments: int = Field(
        ...,
        alias="negativeComments",
        description="Number of negative sentiment comments",
    )
    neutral_comments: int = Field(
        ..., alias="neutralComments", description="Number of neutral sentiment comments"
    )
    average_word_count: float = Field(
        ...,
        alias="averageWordCount",
        description="Average word count across all comments",
    )
    top_commenter_email: str = Field(
        ..., alias="topCommenterEmail", description="Email of the most active commenter"
    )

    # Report content
    report_content: str = Field(
        ..., alias="reportContent", description="Full text report content"
    )

    # Timestamps
    generated_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="generatedAt",
        description="Timestamp when the report was generated (ISO 8601 format)",
    )
    sent_at: Optional[str] = Field(
        default=None,
        alias="sentAt",
        description="Timestamp when the report was sent via email (ISO 8601 format)",
    )

    @field_validator("total_comments")
    @classmethod
    def validate_total_comments(cls, v: int) -> int:
        """Validate total comments is non-negative"""
        if v < 0:
            raise ValueError("Total comments must be non-negative")
        return v

    @field_validator("positive_comments")
    @classmethod
    def validate_positive_comments(cls, v: int) -> int:
        """Validate positive comments is non-negative"""
        if v < 0:
            raise ValueError("Positive comments must be non-negative")
        return v

    @field_validator("negative_comments")
    @classmethod
    def validate_negative_comments(cls, v: int) -> int:
        """Validate negative comments is non-negative"""
        if v < 0:
            raise ValueError("Negative comments must be non-negative")
        return v

    @field_validator("neutral_comments")
    @classmethod
    def validate_neutral_comments(cls, v: int) -> int:
        """Validate neutral comments is non-negative"""
        if v < 0:
            raise ValueError("Neutral comments must be non-negative")
        return v

    @field_validator("average_word_count")
    @classmethod
    def validate_average_word_count(cls, v: float) -> float:
        """Validate average word count is non-negative"""
        if v < 0:
            raise ValueError("Average word count must be non-negative")
        return v

    @field_validator("top_commenter_email")
    @classmethod
    def validate_top_commenter_email(cls, v: str) -> str:
        """Validate top commenter email format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Top commenter email must be non-empty")

        # Basic email validation
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Top commenter email must be a valid email format")

        return v

    @field_validator("report_content")
    @classmethod
    def validate_report_content(cls, v: str) -> str:
        """Validate report content is not empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report content must be non-empty")
        return v.strip()

    def set_sent(self) -> None:
        """Mark the report as sent with current timestamp"""
        self.sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def clear_sent(self) -> None:
        """Clear sent timestamp for retry"""
        self.sent_at = None
        self.update_timestamp()

    def is_sent(self) -> bool:
        """Check if the report has been sent"""
        return self.sent_at is not None

    def validate_sentiment_totals(self) -> bool:
        """Validate that sentiment totals add up to total comments"""
        return (
            self.positive_comments + self.negative_comments + self.neutral_comments
        ) == self.total_comments

    def get_sentiment_percentages(self) -> Dict[str, float]:
        """Calculate sentiment percentages"""
        if self.total_comments == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        return {
            "positive": round((self.positive_comments / self.total_comments) * 100, 2),
            "negative": round((self.negative_comments / self.total_comments) * 100, 2),
            "neutral": round((self.neutral_comments / self.total_comments) * 100, 2),
        }

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
