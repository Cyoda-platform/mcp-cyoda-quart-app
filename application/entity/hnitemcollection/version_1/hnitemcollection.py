# entity/hnitemcollection/version_1/hnitemcollection.py

"""
HNItemCollection for Cyoda Client Application

Manages bulk operations for Hacker News items, including batch uploads,
Firebase API pulls, and collection management as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class HNItemCollection(CyodaEntity):
    """
    HNItemCollection manages bulk operations for Hacker News items.

    Supports batch uploads, Firebase API pulls, and collection management.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending_processing -> processing -> completed/partial_failure/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "HNItemCollection"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core collection fields
    collection_id: Optional[str] = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier for the collection",
    )
    name: str = Field(..., description="Descriptive name for the collection")
    source: str = Field(
        ..., description="Source of items: firebase_api, bulk_upload, manual"
    )

    # Processing metrics
    total_items: int = Field(
        default=0, alias="totalItems", description="Total number of items in collection"
    )
    processed_items: int = Field(
        default=0,
        alias="processedItems",
        description="Number of successfully processed items",
    )
    failed_items: int = Field(
        default=0, alias="failedItems", description="Number of failed items"
    )

    # Collection data
    items: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Array of HNItem references or data"
    )

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Collection creation timestamp",
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )

    # Processing metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional collection metadata"
    )

    # Processing results
    processing_started_at: Optional[str] = Field(
        default=None, alias="processingStartedAt", description="When processing started"
    )
    processing_completed_at: Optional[str] = Field(
        default=None,
        alias="processingCompletedAt",
        description="When processing completed",
    )
    error_details: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="errorDetails", description="Details of processing errors"
    )

    # Validation constants
    ALLOWED_SOURCES: ClassVar[List[str]] = ["firebase_api", "bulk_upload", "manual"]

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate collection source"""
        if v not in cls.ALLOWED_SOURCES:
            raise ValueError(f"Source must be one of: {cls.ALLOWED_SOURCES}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate collection name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Collection name must be non-empty")
        if len(v) > 200:
            raise ValueError("Collection name must be at most 200 characters")
        return v.strip()

    @field_validator("total_items", "processed_items", "failed_items")
    @classmethod
    def validate_counts(cls, v: int) -> int:
        """Validate item counts are non-negative"""
        if v < 0:
            raise ValueError("Item counts must be non-negative")
        return v

    def start_processing(self) -> None:
        """Mark processing as started"""
        self.processing_started_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def complete_processing(self) -> None:
        """Mark processing as completed"""
        self.processing_completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        self.update_timestamp()

    def increment_processed(self) -> None:
        """Increment processed items count"""
        self.processed_items += 1
        self.update_timestamp()

    def increment_failed(self, error_detail: Optional[Dict[str, Any]] = None) -> None:
        """Increment failed items count and optionally add error detail"""
        self.failed_items += 1
        if error_detail:
            if self.error_details is None:
                self.error_details = []
            self.error_details.append(error_detail)
        self.update_timestamp()

    def set_total_items(self, count: int) -> None:
        """Set total items count"""
        self.total_items = count
        self.update_timestamp()

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Add items to the collection"""
        if self.items is None:
            self.items = []
        self.items.extend(items)
        self.total_items = len(self.items)
        self.update_timestamp()

    def get_success_rate(self) -> float:
        """Calculate processing success rate"""
        if self.total_items == 0:
            return 0.0
        return self.processed_items / self.total_items

    def get_failure_rate(self) -> float:
        """Calculate processing failure rate"""
        if self.total_items == 0:
            return 0.0
        return self.failed_items / self.total_items

    def is_processing_complete(self) -> bool:
        """Check if processing is complete"""
        return (self.processed_items + self.failed_items) >= self.total_items

    def has_failures(self) -> bool:
        """Check if there are any processing failures"""
        return self.failed_items > 0

    def all_items_processed_successfully(self) -> bool:
        """Check if all items were processed successfully"""
        return (
            self.total_items > 0
            and self.processed_items == self.total_items
            and self.failed_items == 0
        )

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": self.failed_items,
            "success_rate": self.get_success_rate(),
            "failure_rate": self.get_failure_rate(),
            "is_complete": self.is_processing_complete(),
            "has_failures": self.has_failures(),
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Add state and processing summary for API compatibility
        data["state"] = self.state
        data["processing_summary"] = self.get_processing_summary()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
