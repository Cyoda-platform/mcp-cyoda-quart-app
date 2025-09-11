"""
CommentAnalysisRequest Entity for Cyoda Client Application

Represents a request to analyze comments for a specific post ID from JSONPlaceholder API.
Manages the lifecycle from creation to completion with workflow state management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class CommentAnalysisRequest(CyodaEntity):
    """
    CommentAnalysisRequest represents a request to analyze comments for a specific post ID.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: pending -> fetching_comments -> analyzing -> sending_report -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CommentAnalysisRequest"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    post_id: int = Field(
        ...,
        alias="postId",
        description="The post ID to fetch comments for from JSONPlaceholder API",
    )
    requested_by: str = Field(
        ...,
        alias="requestedBy",
        description="Email address of the user who requested the analysis",
    )

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the request was created (ISO 8601 format)",
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when the analysis was completed (ISO 8601 format)",
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if the analysis failed",
    )

    @field_validator("post_id")
    @classmethod
    def validate_post_id(cls, v: int) -> int:
        """Validate post_id is a positive integer"""
        if v <= 0:
            raise ValueError("Post ID must be a positive integer")
        return v

    @field_validator("requested_by")
    @classmethod
    def validate_requested_by(cls, v: str) -> str:
        """Validate requested_by is a valid email format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Requested by email must be non-empty")

        # Basic email validation
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Requested by must be a valid email format")

        return v

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

    def is_completed(self) -> bool:
        """Check if the request has been completed"""
        return self.completed_at is not None

    def has_error(self) -> bool:
        """Check if the request has an error"""
        return self.error_message is not None

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
