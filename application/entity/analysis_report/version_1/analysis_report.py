"""
AnalysisReport entity for Cyoda Client Application

Represents the analysis report generated from comments.
The entity manages the workflow from report generation to email delivery.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class AnalysisReport(CyodaEntity):
    """
    AnalysisReport represents the analysis report generated from comments.

    The entity state represents the workflow state (GENERATED, SENDING, SENT, FAILED)
    and is managed automatically by the workflow system via entity.meta.state.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "AnalysisReport"
    ENTITY_VERSION: ClassVar[int] = 1

    # Relationship field
    analysis_request_id: str = Field(
        ...,
        alias="analysisRequestId",
        description="Foreign key to the CommentAnalysisRequest",
    )

    # Analysis results
    total_comments: int = Field(
        ...,
        alias="totalComments",
        description="Total number of comments analyzed",
        ge=0,
    )
    average_comment_length: float = Field(
        ...,
        alias="averageCommentLength",
        description="Average length of comments in characters",
        ge=0.0,
    )
    most_active_email_domain: str = Field(
        ...,
        alias="mostActiveEmailDomain",
        description="Email domain that appears most frequently",
    )
    sentiment_summary: str = Field(
        ...,
        alias="sentimentSummary",
        description="Summary of sentiment analysis (e.g., 'Mostly positive')",
    )
    top_keywords: str = Field(
        ..., alias="topKeywords", description="JSON array of most frequent keywords"
    )

    # Timestamp fields
    generated_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="generatedAt",
        description="Timestamp when the report was generated (ISO 8601 format)",
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when the report was sent via email (ISO 8601 format, nullable)",
    )

    @field_validator("analysis_request_id")
    @classmethod
    def validate_analysis_request_id(cls, v: str) -> str:
        """Validate analysis_request_id is non-empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Analysis request ID must be non-empty")
        return v.strip()

    @field_validator("total_comments")
    @classmethod
    def validate_total_comments(cls, v: int) -> int:
        """Validate total_comments is non-negative"""
        if v < 0:
            raise ValueError("Total comments must be non-negative")
        return v

    @field_validator("average_comment_length")
    @classmethod
    def validate_average_comment_length(cls, v: float) -> float:
        """Validate average_comment_length is non-negative"""
        if v < 0.0:
            raise ValueError("Average comment length must be non-negative")
        return v

    @field_validator("most_active_email_domain")
    @classmethod
    def validate_most_active_email_domain(cls, v: str) -> str:
        """Validate most_active_email_domain is non-empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Most active email domain must be non-empty")
        return v.strip().lower()

    @field_validator("sentiment_summary")
    @classmethod
    def validate_sentiment_summary(cls, v: str) -> str:
        """Validate sentiment_summary is non-empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Sentiment summary must be non-empty")
        return v.strip()

    @field_validator("top_keywords")
    @classmethod
    def validate_top_keywords(cls, v: str) -> str:
        """Validate top_keywords is non-empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Top keywords must be non-empty")
        return v.strip()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_email_sent(self) -> None:
        """Mark the report as sent via email with current timestamp"""
        self.email_sent_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def clear_email_sent(self) -> None:
        """Clear email sent timestamp for retry"""
        self.email_sent_at = None
        self.update_timestamp()

    def to_api_response(self) -> dict:
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
