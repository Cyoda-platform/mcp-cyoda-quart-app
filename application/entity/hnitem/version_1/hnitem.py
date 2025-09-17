# entity/hnitem/version_1/hnitem.py

"""
HNItem for Cyoda Client Application

Represents individual Hacker News items from the Firebase HN API, including stories,
comments, jobs, Ask HNs, and polls as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class HNItem(CyodaEntity):
    """
    HNItem represents individual Hacker News items from the Firebase HN API.

    Supports all HN item types: stories, comments, jobs, polls, and pollopts.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending_validation -> validated -> indexed -> active -> archived
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "HNItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core HN API fields
    id: int = Field(..., description="Unique integer identifier from HN API")
    type: str = Field(..., description="Item type: story, comment, job, poll, pollopt")
    by: Optional[str] = Field(default=None, description="Username of the item's author")
    time: Optional[int] = Field(
        default=None, description="Creation date in Unix timestamp"
    )

    # Content fields
    title: Optional[str] = Field(
        default=None, description="Title of the story, poll or job (HTML)"
    )
    text: Optional[str] = Field(
        default=None, description="Comment, story or poll text (HTML)"
    )
    url: Optional[str] = Field(default=None, description="URL of the story")

    # Scoring and metrics
    score: Optional[int] = Field(
        default=None, description="Story's score or votes for pollopt"
    )
    descendants: Optional[int] = Field(
        default=None, description="Total comment count for stories/polls"
    )

    # Relationship fields
    parent: Optional[int] = Field(
        default=None, description="Parent item ID for comments"
    )
    kids: Optional[List[int]] = Field(
        default=None, description="Array of child comment IDs"
    )
    poll: Optional[int] = Field(
        default=None, description="Associated poll ID for pollopts"
    )
    parts: Optional[List[int]] = Field(
        default=None, description="Related pollopt IDs for polls"
    )

    # Status fields
    deleted: Optional[bool] = Field(
        default=None, description="Boolean indicating if item is deleted"
    )
    dead: Optional[bool] = Field(
        default=None, description="Boolean indicating if item is dead"
    )

    # Processing fields (populated during workflow)
    indexed_at: Optional[str] = Field(
        default=None,
        alias="indexedAt",
        description="Timestamp when item was indexed for search",
    )
    validation_status: Optional[str] = Field(
        default=None,
        alias="validationStatus",
        description="Status of validation checks",
    )
    search_content: Optional[str] = Field(
        default=None,
        alias="searchContent",
        description="Processed content for search indexing",
    )

    # Validation constants
    ALLOWED_TYPES: ClassVar[List[str]] = ["story", "comment", "job", "poll", "pollopt"]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate item type according to HN API specification"""
        if v not in cls.ALLOWED_TYPES:
            raise ValueError(f"Type must be one of: {cls.ALLOWED_TYPES}")
        return v

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: int) -> int:
        """Validate HN item ID is positive"""
        if v <= 0:
            raise ValueError("HN item ID must be positive")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: Optional[int]) -> Optional[int]:
        """Validate Unix timestamp if provided"""
        if v is not None and v < 0:
            raise ValueError("Unix timestamp must be non-negative")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate score if provided"""
        if v is not None and v < 0:
            raise ValueError("Score must be non-negative")
        return v

    def update_validation_status(self, status: str) -> None:
        """Update validation status and timestamp"""
        self.validation_status = status
        self.update_timestamp()

    def set_indexed(self) -> None:
        """Mark item as indexed and update timestamp"""
        self.indexed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_search_content(self, content: str) -> None:
        """Set processed search content"""
        self.search_content = content
        self.update_timestamp()

    def is_story(self) -> bool:
        """Check if item is a story"""
        return self.type == "story"

    def is_comment(self) -> bool:
        """Check if item is a comment"""
        return self.type == "comment"

    def is_job(self) -> bool:
        """Check if item is a job posting"""
        return self.type == "job"

    def is_poll(self) -> bool:
        """Check if item is a poll"""
        return self.type == "poll"

    def is_pollopt(self) -> bool:
        """Check if item is a poll option"""
        return self.type == "pollopt"

    def has_children(self) -> bool:
        """Check if item has child comments"""
        return self.kids is not None and len(self.kids) > 0

    def is_deleted_or_dead(self) -> bool:
        """Check if item is deleted or dead"""
        return self.deleted is True or self.dead is True

    def get_display_title(self) -> str:
        """Get display title for the item"""
        if self.title:
            return self.title
        elif self.text and len(self.text) > 50:
            return self.text[:50] + "..."
        elif self.text:
            return self.text
        else:
            return f"HN Item {self.id}"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
