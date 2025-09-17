# entity/hnitemcollection/version_1/hnitemcollection.py

"""
HNItemCollection Entity for Cyoda Client Application

Manages bulk operations for HN items including array uploads, file uploads,
and batch processing from Firebase HN API.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class HNItemCollection(CyodaEntity):
    """
    HNItemCollection manages bulk operations for HN items.

    Supports array uploads, file uploads, and batch processing from Firebase HN API.
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> received -> processing -> completed/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "HNItemCollection"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core collection fields
    collection_id: Optional[str] = Field(
        default=None, description="Unique identifier for the collection"
    )
    collection_type: str = Field(
        ..., description="Type of collection: array, file_upload, firebase_pull"
    )
    source: Optional[str] = Field(
        default=None, description="Source description (filename, API endpoint, etc.)"
    )

    # Item counts
    total_items: int = Field(
        default=0, description="Total number of items in collection"
    )
    processed_items: int = Field(
        default=0, description="Number of successfully processed items"
    )
    failed_items: int = Field(default=0, description="Number of failed items")

    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        description="Collection creation timestamp",
    )
    completed_at: Optional[str] = Field(
        default=None, description="Collection completion timestamp"
    )

    # Data and results
    items: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Array of HNItem references or data"
    )
    processing_errors: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Array of error details"
    )

    # Processing metadata
    batch_size: Optional[int] = Field(
        default=100, description="Number of items to process in each batch"
    )
    processing_started_at: Optional[str] = Field(
        default=None, description="When processing started"
    )
    processing_duration_ms: Optional[int] = Field(
        default=None, description="Total processing time in milliseconds"
    )

    # Firebase API specific fields
    firebase_endpoint: Optional[str] = Field(
        default=None, description="Firebase API endpoint used for pulling data"
    )
    firebase_filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Filters applied when pulling from Firebase"
    )

    # File upload specific fields
    file_name: Optional[str] = Field(
        default=None, description="Original filename for file uploads"
    )
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    file_format: Optional[str] = Field(
        default=None, description="File format: json, csv, etc."
    )

    # Validation constants
    ALLOWED_COLLECTION_TYPES: ClassVar[List[str]] = [
        "array",
        "file_upload",
        "firebase_pull",
    ]

    @field_validator("collection_type")
    @classmethod
    def validate_collection_type(cls, v: str) -> str:
        """Validate collection type"""
        if v not in cls.ALLOWED_COLLECTION_TYPES:
            raise ValueError(
                f"Collection type must be one of: {cls.ALLOWED_COLLECTION_TYPES}"
            )
        return v

    @field_validator("total_items")
    @classmethod
    def validate_total_items(cls, v: int) -> int:
        """Validate total items count is non-negative"""
        if v < 0:
            raise ValueError("Total items must be non-negative")
        return v

    @field_validator("processed_items")
    @classmethod
    def validate_processed_items(cls, v: int) -> int:
        """Validate processed items count is non-negative"""
        if v < 0:
            raise ValueError("Processed items must be non-negative")
        return v

    @field_validator("failed_items")
    @classmethod
    def validate_failed_items(cls, v: int) -> int:
        """Validate failed items count is non-negative"""
        if v < 0:
            raise ValueError("Failed items must be non-negative")
        return v

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate batch size is positive"""
        if v is not None and v <= 0:
            raise ValueError("Batch size must be positive")
        return v

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100

    def get_failure_rate(self) -> float:
        """Calculate failure rate as percentage"""
        if self.total_items == 0:
            return 0.0
        return (self.failed_items / self.total_items) * 100

    def is_processing_complete(self) -> bool:
        """Check if processing is complete"""
        return (self.processed_items + self.failed_items) >= self.total_items

    def is_array_collection(self) -> bool:
        """Check if this is an array collection"""
        return self.collection_type == "array"

    def is_file_upload(self) -> bool:
        """Check if this is a file upload collection"""
        return self.collection_type == "file_upload"

    def is_firebase_pull(self) -> bool:
        """Check if this is a Firebase pull collection"""
        return self.collection_type == "firebase_pull"

    def add_processing_error(self, error: Dict[str, Any]) -> None:
        """Add a processing error to the collection"""
        if self.processing_errors is None:
            self.processing_errors = []
        self.processing_errors.append(error)
        self.failed_items += 1

    def increment_processed(self) -> None:
        """Increment the processed items counter"""
        self.processed_items += 1

    def start_processing(self) -> None:
        """Mark processing as started"""
        self.processing_started_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def complete_processing(self) -> None:
        """Mark processing as completed"""
        self.completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Calculate processing duration if start time is available
        if self.processing_started_at:
            start_time = datetime.fromisoformat(
                self.processing_started_at.replace("Z", "+00:00")
            )
            end_time = datetime.now(timezone.utc)
            duration = end_time - start_time
            self.processing_duration_ms = int(duration.total_seconds() * 1000)

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of processing results"""
        return {
            "collection_id": self.collection_id,
            "collection_type": self.collection_type,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "failed_items": self.failed_items,
            "success_rate": self.get_success_rate(),
            "failure_rate": self.get_failure_rate(),
            "is_complete": self.is_processing_complete(),
            "processing_duration_ms": self.processing_duration_ms,
            "error_count": len(self.processing_errors) if self.processing_errors else 0,
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Add state for API compatibility
        data["state"] = self.state
        # Add processing summary
        data["processing_summary"] = self.get_processing_summary()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
