"""
Comment entity for Cyoda Client Application

Represents a comment fetched from the JSONPlaceholder API.
Comments are static data with no workflow state needed.
"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Comment(CyodaEntity):
    """
    Comment represents a comment fetched from the JSONPlaceholder API.

    Comments are fetched from external API and stored for analysis.
    No workflow state needed as comments are static data.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Comment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Fields from JSONPlaceholder API
    comment_id: int = Field(
        ..., alias="id", description="Unique identifier for the comment (from API)"
    )
    post_id: int = Field(
        ..., alias="postId", description="The post ID this comment belongs to"
    )
    name: str = Field(..., description="Name/title of the comment")
    email: str = Field(..., description="Email address of the comment author")
    body: str = Field(..., description="Content/body of the comment")

    # Relationship fields
    analysis_request_id: Optional[str] = Field(
        default=None,
        alias="analysisRequestId",
        description="Foreign key to the CommentAnalysisRequest",
    )

    # Timestamp field
    fetched_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="fetchedAt",
        description="Timestamp when the comment was fetched (ISO 8601 format)",
    )

    @field_validator("comment_id")
    @classmethod
    def validate_comment_id(cls, v: int) -> int:
        """Validate comment_id is a positive integer"""
        if v <= 0:
            raise ValueError("Comment ID must be a positive integer")
        return v

    @field_validator("post_id")
    @classmethod
    def validate_post_id(cls, v: int) -> int:
        """Validate post_id is a positive integer"""
        if v <= 0:
            raise ValueError("Post ID must be a positive integer")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name must be non-empty")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email must be non-empty")

        # Basic email validation
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("Email must contain @ symbol")

        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        """Validate body field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Body must be non-empty")
        return v.strip()

    def get_email_domain(self) -> str:
        """Extract domain from email address"""
        if "@" in self.email:
            return self.email.split("@")[-1]
        return ""

    def get_body_length(self) -> int:
        """Get the length of the comment body"""
        return len(self.body)

    def to_api_response(self) -> dict:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility (comments don't have workflow states)
        data["state"] = self.state or "static"
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
