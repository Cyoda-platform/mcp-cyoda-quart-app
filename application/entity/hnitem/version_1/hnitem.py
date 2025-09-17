# entity/hnitem/version_1/hnitem.py

"""
HNItem Entity for Cyoda Client Application

Represents a single Hacker News item in Firebase HN API JSON format.
Supports all item types: stories, comments, jobs, Ask HNs, polls, and poll options.
"""

from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class HNItem(CyodaEntity):
    """
    HNItem represents a single Hacker News item from Firebase HN API.

    Supports all item types: stories, comments, jobs, Ask HNs, polls, and poll options.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending -> validated -> stored -> indexed -> published
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "HNItem"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core Firebase HN API fields
    id: Optional[int] = Field(
        default=None, description="Unique integer identifier from HN API"
    )
    type: Optional[str] = Field(
        default=None, description="Item type: job, story, comment, poll, pollopt"
    )
    by: Optional[str] = Field(default=None, description="Username of the item's author")
    time: Optional[int] = Field(
        default=None, description="Creation date of the item, in Unix Time"
    )

    # Content fields
    title: Optional[str] = Field(
        default=None, description="The title of the story, poll or job. HTML"
    )
    text: Optional[str] = Field(
        default=None, description="The comment, story or poll text. HTML"
    )
    url: Optional[str] = Field(default=None, description="The URL of the story")

    # Scoring and engagement
    score: Optional[int] = Field(
        default=None, description="The story's score, or the votes for a pollopt"
    )
    descendants: Optional[int] = Field(
        default=None, description="Total comment count for stories"
    )

    # Relationships
    parent: Optional[int] = Field(
        default=None,
        description="The comment's parent: either another comment or the relevant story",
    )
    kids: Optional[List[int]] = Field(
        default=None,
        description="The ids of the item's comments, in ranked display order",
    )

    # Poll-specific fields
    poll: Optional[int] = Field(
        default=None, description="The pollopt's associated poll"
    )
    parts: Optional[List[int]] = Field(
        default=None, description="A list of related pollopts, in display order"
    )

    # Status fields
    deleted: Optional[bool] = Field(
        default=None, description="True if the item is deleted"
    )
    dead: Optional[bool] = Field(default=None, description="True if the item is dead")

    # Processing fields (populated during workflow)
    validation_error: Optional[str] = Field(
        default=None, description="Validation error message if validation fails"
    )
    validation_status: Optional[str] = Field(
        default=None, description="Validation status: valid, invalid, pending"
    )
    processed_time: Optional[str] = Field(
        default=None, description="Timestamp when item was processed"
    )
    search_text: Optional[str] = Field(
        default=None, description="Combined searchable text from title and text fields"
    )
    parent_chain: Optional[List[int]] = Field(
        default=None, description="Chain of parent IDs for hierarchy traversal"
    )
    stored_at: Optional[str] = Field(
        default=None, description="Timestamp when item was stored"
    )
    storage_status: Optional[str] = Field(
        default=None, description="Storage status: persisted, failed"
    )
    indexed_at: Optional[str] = Field(
        default=None, description="Timestamp when item was indexed for search"
    )

    # Validation constants
    ALLOWED_TYPES: ClassVar[List[str]] = ["job", "story", "comment", "poll", "pollopt"]

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate item type according to HN API specification"""
        if v is not None and v not in cls.ALLOWED_TYPES:
            raise ValueError(f"Type must be one of: {cls.ALLOWED_TYPES}")
        return v

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate HN item ID is positive integer"""
        if v is not None and v <= 0:
            raise ValueError("HN item ID must be a positive integer")
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v: Optional[int]) -> Optional[int]:
        """Validate Unix timestamp is positive"""
        if v is not None and v <= 0:
            raise ValueError("Time must be a positive Unix timestamp")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate score is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Score must be non-negative")
        return v

    @field_validator("descendants")
    @classmethod
    def validate_descendants(cls, v: Optional[int]) -> Optional[int]:
        """Validate descendants count is non-negative"""
        if v is not None and v < 0:
            raise ValueError("Descendants count must be non-negative")
        return v

    def is_story(self) -> bool:
        """Check if this item is a story"""
        return self.type == "story"

    def is_comment(self) -> bool:
        """Check if this item is a comment"""
        return self.type == "comment"

    def is_job(self) -> bool:
        """Check if this item is a job posting"""
        return self.type == "job"

    def is_poll(self) -> bool:
        """Check if this item is a poll"""
        return self.type == "poll"

    def is_poll_option(self) -> bool:
        """Check if this item is a poll option"""
        return self.type == "pollopt"

    def has_children(self) -> bool:
        """Check if this item has child comments"""
        return self.kids is not None and len(self.kids) > 0

    def is_top_level(self) -> bool:
        """Check if this is a top-level item (no parent)"""
        return self.parent is None

    def get_display_text(self) -> str:
        """Get the primary display text for this item"""
        if self.title:
            return self.title
        elif self.text:
            return self.text[:100] + "..." if len(self.text) > 100 else self.text
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
