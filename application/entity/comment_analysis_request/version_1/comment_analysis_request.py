"""
CommentAnalysisRequest entity for Cyoda Client Application

Represents a request to analyze comments for a specific post ID from JSONPlaceholder API.
The entity manages the workflow from comment fetching through analysis to email reporting.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CommentAnalysisRequest(CyodaEntity):
    """
    CommentAnalysisRequest represents a request to analyze comments for a specific post ID.

    The entity state represents the workflow state (PENDING, FETCHING_COMMENTS, ANALYZING,
    SENDING_REPORT, COMPLETED, FAILED) and is managed automatically by the workflow system
    via entity.meta.state.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CommentAnalysisRequest"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    post_id: int = Field(
        ...,
        alias="postId",
        description="The post ID to fetch comments for from JSONPlaceholder API",
        gt=0,
    )
    recipient_email: str = Field(
        ...,
        alias="recipientEmail",
        description="Email address to send the analysis report to",
    )

    # Timestamp fields
    requested_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="requestedAt",
        description="Timestamp when the request was created (ISO 8601 format)",
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when the analysis was completed (ISO 8601 format, nullable)",
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if the analysis failed (nullable)",
    )

    @field_validator("post_id")
    @classmethod
    def validate_post_id(cls, v: int) -> int:
        """Validate post_id is a positive integer"""
        if v <= 0:
            raise ValueError("Post ID must be a positive integer")
        return v

    @field_validator("recipient_email")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        """Validate recipient_email is a valid email format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Recipient email must be non-empty")

        # Basic email validation
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Recipient email must be a valid email format")

        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_completed(self) -> None:
        """Mark the request as completed with current timestamp"""
        self.completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def set_error(self, error_message: str) -> None:
        """Set error message and update timestamp"""
        self.error_message = error_message
        self.update_timestamp()

    def clear_error(self) -> None:
        """Clear error message for retry"""
        self.error_message = None
        self.completed_at = None
        self.update_timestamp()

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
