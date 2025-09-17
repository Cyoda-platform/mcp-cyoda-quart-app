# entity/hnitem/version_1/hnitem.py

"""
HnItem for Cyoda Client Application

Represents individual Hacker News items following the Firebase HN API JSON format.
Supports stories, comments, jobs, Ask HNs, polls, and poll options.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class HnItem(CyodaEntity):
    """
    HnItem represents individual Hacker News items following the Firebase HN API format.

    Supports all HN item types: story, comment, job, poll, pollopt
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: pending -> validating -> validated -> storing -> stored
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "HnItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from Firebase HN API
    id: int = Field(..., description="The item's unique id")
    type: str = Field(
        ..., description="The type of item: job, story, comment, poll, or pollopt"
    )

    # Optional fields from Firebase HN API
    deleted: Optional[bool] = Field(
        default=None, description="true if the item is deleted"
    )
    by: Optional[str] = Field(
        default=None, description="The username of the item's author"
    )
    time: Optional[int] = Field(
        default=None, description="Creation date of the item, in Unix Time"
    )
    text: Optional[str] = Field(
        default=None, description="The comment, story or poll text. HTML"
    )
    dead: Optional[bool] = Field(default=None, description="true if the item is dead")
    parent: Optional[int] = Field(
        default=None,
        description="The comment's parent: either another comment or the relevant story",
    )
    poll: Optional[int] = Field(
        default=None, description="The pollopt's associated poll"
    )
    kids: Optional[List[int]] = Field(
        default=None,
        description="The ids of the item's comments, in ranked display order",
    )
    url: Optional[str] = Field(default=None, description="The URL of the story")
    score: Optional[int] = Field(
        default=None, description="The story's score, or the votes for a pollopt"
    )
    title: Optional[str] = Field(
        default=None, description="The title of the story, poll or job. HTML"
    )
    parts: Optional[List[int]] = Field(
        default=None, description="A list of related pollopts, in display order"
    )
    descendants: Optional[int] = Field(
        default=None,
        description="In the case of stories or polls, the total comment count",
    )

    # System attributes
    source: Optional[str] = Field(
        default="manual_post",
        description="Source of the item: firebase_api, manual_post, bulk_upload",
    )
    imported_at: Optional[int] = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp()),
        description="Unix timestamp when item was imported",
    )
    last_updated: Optional[int] = Field(
        default=None, description="Unix timestamp when item was last updated"
    )

    # Processing-related fields (populated during workflow)
    validation_errors: Optional[List[str]] = Field(
        default=None, description="List of validation errors if any"
    )
    validation_status: Optional[str] = Field(
        default=None, description="Validation status: passed, failed"
    )
    validated_at: Optional[int] = Field(
        default=None, description="Unix timestamp when validation completed"
    )
    storage_status: Optional[str] = Field(
        default=None, description="Storage status: success, failed"
    )
    storage_action: Optional[str] = Field(
        default=None, description="Storage action taken: created, updated"
    )
    storage_error: Optional[str] = Field(
        default=None, description="Storage error message if failed"
    )
    stored_at: Optional[int] = Field(
        default=None, description="Unix timestamp when item was stored"
    )
    processing_completed_at: Optional[int] = Field(
        default=None, description="Unix timestamp when processing completed"
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Reason for failure: validation_failed, storage_failed",
    )
    failure_details: Optional[str] = Field(
        default=None, description="Detailed failure information"
    )
    failed_at: Optional[int] = Field(
        default=None, description="Unix timestamp when failure occurred"
    )
    retry_count: Optional[int] = Field(
        default=0, description="Number of retry attempts"
    )
    retry_attempted_at: Optional[int] = Field(
        default=None, description="Unix timestamp of last retry attempt"
    )
    status: Optional[str] = Field(
        default="pending", description="Item status: pending, active, archived"
    )

    # Validation constants
    ALLOWED_TYPES: ClassVar[List[str]] = ["job", "story", "comment", "poll", "pollopt"]
    ALLOWED_SOURCES: ClassVar[List[str]] = [
        "firebase_api",
        "manual_post",
        "bulk_upload",
    ]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate type field"""
        if v not in cls.ALLOWED_TYPES:
            raise ValueError(f"Type must be one of: {cls.ALLOWED_TYPES}")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate source field"""
        if v is not None and v not in cls.ALLOWED_SOURCES:
            raise ValueError(f"Source must be one of: {cls.ALLOWED_SOURCES}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "HnItem":
        """Validate business logic rules"""
        # Comments must have a parent (except for top-level comments which can be stories)
        if self.type == "comment" and self.parent is None:
            # Allow comments without parent for now, validation will be done in processor
            pass

        # Poll options must reference a poll
        if self.type == "pollopt" and self.poll is None:
            # Allow for now, validation will be done in processor
            pass

        # Only certain types can have scores
        if self.score is not None and self.type not in [
            "story",
            "poll",
            "job",
            "pollopt",
        ]:
            raise ValueError(f"Type {self.type} cannot have a score")

        return self

    def update_last_updated(self) -> None:
        """Update the last_updated timestamp to current time"""
        self.last_updated = int(datetime.now(timezone.utc).timestamp())

    def set_validation_result(
        self, status: str, errors: Optional[List[str]] = None
    ) -> None:
        """Set validation result and update timestamp"""
        self.validation_status = status
        self.validation_errors = errors or []
        self.validated_at = int(datetime.now(timezone.utc).timestamp())
        self.update_last_updated()

    def set_storage_result(
        self, status: str, action: Optional[str] = None, error: Optional[str] = None
    ) -> None:
        """Set storage result and update timestamp"""
        self.storage_status = status
        self.storage_action = action
        self.storage_error = error
        if status == "success":
            self.stored_at = int(datetime.now(timezone.utc).timestamp())
        self.update_last_updated()

    def set_failure(self, reason: str, details: Optional[str] = None) -> None:
        """Set failure information and update timestamp"""
        self.failure_reason = reason
        self.failure_details = details
        self.failed_at = int(datetime.now(timezone.utc).timestamp())
        self.retry_count = (self.retry_count or 0) + 1
        self.update_last_updated()

    def reset_for_retry(self) -> None:
        """Reset item for retry processing"""
        self.validation_errors = None
        self.storage_error = None
        self.failure_reason = None
        self.failure_details = None
        self.validation_status = None
        self.storage_status = None
        self.retry_attempted_at = int(datetime.now(timezone.utc).timestamp())
        self.update_last_updated()

    def is_valid(self) -> bool:
        """Check if item has passed validation"""
        return self.validation_status == "passed" and not self.validation_errors

    def is_stored(self) -> bool:
        """Check if item has been successfully stored"""
        return self.storage_status == "success" and self.stored_at is not None

    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if item can be retried"""
        return (self.retry_count or 0) < max_retries and self.failure_reason in [
            "validation_failed",
            "storage_failed",
        ]

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
