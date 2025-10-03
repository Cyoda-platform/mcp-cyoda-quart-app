# entity/data_extraction/version_1/data_extraction.py

"""
DataExtraction Entity for Pet Store Performance Analysis System

Tracks API data extraction jobs and their status for automated data collection
from Pet Store API as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction represents a data extraction job from external APIs.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> started -> completed -> processed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core extraction job fields
    job_name: str = Field(..., alias="jobName", description="Name of the extraction job")
    api_source: str = Field(
        default="petstore",
        alias="apiSource",
        description="Source API identifier"
    )
    api_endpoint: str = Field(
        ...,
        alias="apiEndpoint",
        description="API endpoint URL for data extraction"
    )
    extraction_type: str = Field(
        default="scheduled",
        alias="extractionType",
        description="Type of extraction (scheduled, manual, on_demand)"
    )
    
    # Scheduling information
    scheduled_for: Optional[str] = Field(
        default=None,
        alias="scheduledFor",
        description="Scheduled execution time (ISO 8601 format)"
    )
    frequency: Optional[str] = Field(
        default="weekly",
        description="Extraction frequency (daily, weekly, monthly)"
    )
    
    # Execution tracking
    started_at: Optional[str] = Field(
        default=None,
        alias="startedAt",
        description="Timestamp when extraction started"
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when extraction completed"
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        alias="durationSeconds",
        description="Extraction duration in seconds"
    )
    
    # Results tracking
    records_extracted: Optional[int] = Field(
        default=None,
        alias="recordsExtracted",
        description="Number of records successfully extracted"
    )
    records_processed: Optional[int] = Field(
        default=None,
        alias="recordsProcessed",
        description="Number of records successfully processed"
    )
    records_failed: Optional[int] = Field(
        default=None,
        alias="recordsFailed",
        description="Number of records that failed processing"
    )
    
    # Status and error tracking
    extraction_status: str = Field(
        default="pending",
        alias="extractionStatus",
        description="Current status of extraction job"
    )
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if extraction failed"
    )
    retry_count: Optional[int] = Field(
        default=0,
        alias="retryCount",
        description="Number of retry attempts"
    )
    
    # Configuration and metadata
    extraction_config: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="extractionConfig",
        description="Configuration parameters for extraction"
    )
    api_response_format: Optional[str] = Field(
        default="json",
        alias="apiResponseFormat",
        description="Expected API response format (json, xml)"
    )
    
    # Data quality metrics
    data_quality_score: Optional[float] = Field(
        default=None,
        alias="dataQualityScore",
        description="Data quality score (0-100)"
    )
    validation_errors: Optional[List[str]] = Field(
        default=None,
        alias="validationErrors",
        description="List of data validation errors"
    )

    # Validation rules
    ALLOWED_EXTRACTION_TYPES: ClassVar[List[str]] = [
        "scheduled", "manual", "on_demand"
    ]
    
    ALLOWED_FREQUENCIES: ClassVar[List[str]] = [
        "daily", "weekly", "monthly"
    ]
    
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "pending", "running", "completed", "failed", "cancelled"
    ]
    
    ALLOWED_FORMATS: ClassVar[List[str]] = [
        "json", "xml", "csv"
    ]

    @field_validator("job_name")
    @classmethod
    def validate_job_name(cls, v: str) -> str:
        """Validate job name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Job name must be non-empty")
        if len(v) > 100:
            raise ValueError("Job name must be at most 100 characters")
        return v.strip()

    @field_validator("extraction_type")
    @classmethod
    def validate_extraction_type(cls, v: str) -> str:
        """Validate extraction type"""
        if v not in cls.ALLOWED_EXTRACTION_TYPES:
            raise ValueError(f"Extraction type must be one of: {cls.ALLOWED_EXTRACTION_TYPES}")
        return v

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate frequency"""
        if v is not None and v not in cls.ALLOWED_FREQUENCIES:
            raise ValueError(f"Frequency must be one of: {cls.ALLOWED_FREQUENCIES}")
        return v

    @field_validator("extraction_status")
    @classmethod
    def validate_extraction_status(cls, v: str) -> str:
        """Validate extraction status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Extraction status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("api_response_format")
    @classmethod
    def validate_api_response_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate API response format"""
        if v is not None and v not in cls.ALLOWED_FORMATS:
            raise ValueError(f"API response format must be one of: {cls.ALLOWED_FORMATS}")
        return v

    def start_extraction(self) -> None:
        """Mark extraction as started"""
        self.extraction_status = "running"
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def complete_extraction(self, records_extracted: int, records_processed: int, records_failed: int = 0) -> None:
        """Mark extraction as completed with results"""
        self.extraction_status = "completed"
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.records_extracted = records_extracted
        self.records_processed = records_processed
        self.records_failed = records_failed
        
        # Calculate duration if started_at is available
        if self.started_at:
            start_time = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end_time = datetime.now(timezone.utc)
            self.duration_seconds = int((end_time - start_time).total_seconds())

    def fail_extraction(self, error_message: str) -> None:
        """Mark extraction as failed with error message"""
        self.extraction_status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def increment_retry_count(self) -> None:
        """Increment retry count"""
        if self.retry_count is None:
            self.retry_count = 0
        self.retry_count += 1

    def set_data_quality_score(self, score: float) -> None:
        """Set data quality score (0-100)"""
        if score < 0 or score > 100:
            raise ValueError("Data quality score must be between 0 and 100")
        self.data_quality_score = score

    def add_validation_error(self, error: str) -> None:
        """Add a validation error to the list"""
        if self.validation_errors is None:
            self.validation_errors = []
        self.validation_errors.append(error)

    def is_successful(self) -> bool:
        """Check if extraction was successful"""
        return self.extraction_status == "completed" and self.error_message is None

    def get_success_rate(self) -> Optional[float]:
        """Calculate success rate of processed records"""
        if self.records_extracted is None or self.records_extracted == 0:
            return None
        
        processed = self.records_processed or 0
        return (processed / self.records_extracted) * 100

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
