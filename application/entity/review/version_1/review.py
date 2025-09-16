"""
Review Entity for Purrfect Pets API

Represents a customer review for a pet with rating and comments.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Review(CyodaEntity):
    """
    Review entity representing customer reviews for pets.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: Pending -> Approved -> Rejected
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Review"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    pet_id: int = Field(..., description="Foreign key to Pet")
    user_id: int = Field(..., description="Foreign key to User")
    rating: int = Field(..., description="Rating from 1 to 5", ge=1, le=5)
    comment: str = Field(..., description="Review comment", max_length=1000)
    helpful_count: int = Field(default=0, description="Number of helpful votes", ge=0)

    # Timestamps (inherited from CyodaEntity but override for consistency)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Timestamp when the review was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the review was last updated (ISO 8601 format)",
    )

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating"""
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        """Validate comment"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Review comment must be non-empty")
        if len(v) > 1000:
            raise ValueError("Review comment must be at most 1000 characters long")
        return v.strip()

    @field_validator("helpful_count")
    @classmethod
    def validate_helpful_count(cls, v: int) -> int:
        """Validate helpful count"""
        if v < 0:
            raise ValueError("Helpful count must be non-negative")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def increment_helpful_count(self) -> None:
        """Increment the helpful count"""
        self.helpful_count += 1
        self.update_timestamp()

    def decrement_helpful_count(self) -> None:
        """Decrement the helpful count (minimum 0)"""
        if self.helpful_count > 0:
            self.helpful_count -= 1
            self.update_timestamp()

    def is_pending(self) -> bool:
        """Check if review is pending moderation"""
        return self.state == "Pending"

    def is_approved(self) -> bool:
        """Check if review is approved"""
        return self.state == "Approved"

    def is_rejected(self) -> bool:
        """Check if review is rejected"""
        return self.state == "Rejected"

    def is_high_rating(self) -> bool:
        """Check if review has high rating (4-5 stars)"""
        return self.rating >= 4

    def is_low_rating(self) -> bool:
        """Check if review has low rating (1-2 stars)"""
        return self.rating <= 2

    def is_helpful(self) -> bool:
        """Check if review has been marked as helpful by others"""
        return self.helpful_count > 0

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump()
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
