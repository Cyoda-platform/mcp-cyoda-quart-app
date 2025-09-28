# entity/comment_analysis_report/version_1/comment_analysis_report.py

"""
CommentAnalysisReport Entity for Cyoda Client Application

Represents aggregated analysis results from comments for a specific post
with email reporting status and summary statistics.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CommentAnalysisReport(CyodaEntity):
    """
    CommentAnalysisReport entity represents aggregated analysis results
    for comments from a specific post, including email reporting status.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: none -> created -> analyzed -> emailed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CommentAnalysisReport"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report identification
    post_id: int = Field(..., alias="postId", description="ID of the post this report analyzes")
    report_title: str = Field(..., alias="reportTitle", description="Title of the analysis report")
    
    # Analysis summary statistics
    total_comments: int = Field(
        default=0,
        alias="totalComments",
        description="Total number of comments analyzed"
    )
    positive_comments: int = Field(
        default=0,
        alias="positiveComments",
        description="Number of comments with positive sentiment"
    )
    negative_comments: int = Field(
        default=0,
        alias="negativeComments",
        description="Number of comments with negative sentiment"
    )
    neutral_comments: int = Field(
        default=0,
        alias="neutralComments",
        description="Number of comments with neutral sentiment"
    )
    
    # Detailed analysis results
    average_sentiment_score: Optional[float] = Field(
        default=None,
        alias="averageSentimentScore",
        description="Average sentiment score across all comments (-1.0 to 1.0)"
    )
    most_common_keywords: Optional[List[str]] = Field(
        default=None,
        alias="mostCommonKeywords",
        description="List of most frequently mentioned keywords"
    )
    average_word_count: Optional[float] = Field(
        default=None,
        alias="averageWordCount",
        description="Average word count per comment"
    )
    
    # Email reporting
    recipient_email: str = Field(..., alias="recipientEmail", description="Email address to send report to")
    email_sent: bool = Field(
        default=False,
        alias="emailSent",
        description="Whether the report has been sent via email"
    )
    email_sent_at: Optional[str] = Field(
        default=None,
        alias="emailSentAt",
        description="Timestamp when email was sent (ISO 8601 format)"
    )
    email_subject: Optional[str] = Field(
        default=None,
        alias="emailSubject",
        description="Subject line of the email report"
    )
    
    # Report generation metadata
    generated_at: Optional[str] = Field(
        default=None,
        alias="generatedAt",
        description="Timestamp when report was generated (ISO 8601 format)"
    )
    report_version: str = Field(
        default="1.0",
        alias="reportVersion",
        description="Version of report generation algorithm"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the report was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the report was last updated (ISO 8601 format)",
    )

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Basic email validation"""
        if not v or "@" not in v:
            raise ValueError("Recipient email must contain @ symbol")
        return v.strip().lower()

    @field_validator("report_title")
    @classmethod
    def validate_report_title(cls, v: str) -> str:
        """Validate report title"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title cannot be empty")
        if len(v) > 200:
            raise ValueError("Report title too long (max 200 characters)")
        return v.strip()

    @field_validator("average_sentiment_score")
    @classmethod
    def validate_average_sentiment_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate average sentiment score range"""
        if v is not None and (v < -1.0 or v > 1.0):
            raise ValueError("Average sentiment score must be between -1.0 and 1.0")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_analysis_results(
        self,
        total_comments: int,
        positive_comments: int,
        negative_comments: int,
        neutral_comments: int,
        average_sentiment_score: float,
        most_common_keywords: List[str],
        average_word_count: float
    ) -> None:
        """Set analysis results and update timestamps"""
        self.total_comments = total_comments
        self.positive_comments = positive_comments
        self.negative_comments = negative_comments
        self.neutral_comments = neutral_comments
        self.average_sentiment_score = average_sentiment_score
        self.most_common_keywords = most_common_keywords
        self.average_word_count = average_word_count
        self.generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_email_sent(self, email_subject: str) -> None:
        """Mark the report as sent via email"""
        self.email_sent = True
        self.email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.email_subject = email_subject
        self.update_timestamp()

    def is_complete(self) -> bool:
        """Check if report is complete with analysis results"""
        return (
            self.total_comments > 0 and
            self.average_sentiment_score is not None and
            self.generated_at is not None
        )

    def get_sentiment_distribution(self) -> Dict[str, float]:
        """Get sentiment distribution as percentages"""
        if self.total_comments == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        
        return {
            "positive": (self.positive_comments / self.total_comments) * 100,
            "negative": (self.negative_comments / self.total_comments) * 100,
            "neutral": (self.neutral_comments / self.total_comments) * 100,
        }

    def get_business_id(self) -> str:
        """Get business identifier for this report"""
        return f"report_post_{self.post_id}"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        # Add calculated sentiment distribution
        data["sentimentDistribution"] = self.get_sentiment_distribution()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
