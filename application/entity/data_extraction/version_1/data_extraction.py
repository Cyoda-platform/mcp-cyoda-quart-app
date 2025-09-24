# entity/data_extraction/version_1/data_extraction.py

"""
DataExtraction Entity for Product Performance Analysis and Reporting System

Represents data extraction jobs that fetch product data from the Pet Store API.
Tracks extraction status, schedules, and metadata for automated data collection.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction entity represents data extraction jobs from Pet Store API.
    
    Tracks the automated data collection process including:
    - Extraction scheduling and execution
    - API connection details and status
    - Data quality metrics and error handling
    - Integration with product analysis workflow
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Extraction job metadata
    job_name: str = Field(..., alias="jobName", description="Name of the extraction job")
    extraction_type: str = Field(
        default="scheduled",
        alias="extractionType",
        description="Type of extraction (scheduled, manual, on_demand)"
    )
    schedule: str = Field(
        default="weekly_monday",
        description="Extraction schedule (weekly_monday, daily, monthly)"
    )
    
    # API configuration
    api_url: str = Field(
        default="https://petstore.swagger.io/v2",
        alias="apiUrl",
        description="Pet Store API base URL"
    )
    api_endpoints: List[str] = Field(
        default_factory=lambda: ["/store/inventory", "/pet/findByStatus"],
        alias="apiEndpoints",
        description="List of API endpoints to extract data from"
    )
    data_format: str = Field(
        default="json",
        alias="dataFormat",
        description="Expected data format (json, xml)"
    )
    
    # Execution status and timing
    status: str = Field(
        default="pending",
        description="Current extraction status"
    )
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
    
    # Data extraction results
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
    
    # Error handling and quality metrics
    error_count: int = Field(
        default=0,
        alias="errorCount",
        description="Number of errors encountered during extraction"
    )
    error_messages: Optional[List[str]] = Field(
        default=None,
        alias="errorMessages",
        description="List of error messages encountered"
    )
    data_quality_score: Optional[float] = Field(
        default=None,
        alias="dataQualityScore",
        description="Data quality score (0-100)"
    )
    
    # API response metadata
    api_response_time: Optional[float] = Field(
        default=None,
        alias="apiResponseTime",
        description="Average API response time in milliseconds"
    )
    api_status_code: Optional[int] = Field(
        default=None,
        alias="apiStatusCode",
        description="Last API response status code"
    )
    
    # Scheduling information
    next_scheduled_run: Optional[str] = Field(
        default=None,
        alias="nextScheduledRun",
        description="Timestamp of next scheduled extraction"
    )
    last_successful_run: Optional[str] = Field(
        default=None,
        alias="lastSuccessfulRun",
        description="Timestamp of last successful extraction"
    )
    
    # Configuration and settings
    retry_count: int = Field(
        default=0,
        alias="retryCount",
        description="Number of retry attempts made"
    )
    max_retries: int = Field(
        default=3,
        alias="maxRetries",
        description="Maximum number of retry attempts"
    )
    timeout_seconds: int = Field(
        default=300,
        alias="timeoutSeconds",
        description="Extraction timeout in seconds"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the extraction job was created",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the extraction job was last updated",
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "pending", "running", "completed", "failed", "cancelled", "retrying"
    ]
    ALLOWED_EXTRACTION_TYPES: ClassVar[List[str]] = [
        "scheduled", "manual", "on_demand", "retry"
    ]
    ALLOWED_DATA_FORMATS: ClassVar[List[str]] = ["json", "xml"]

    @field_validator("job_name")
    @classmethod
    def validate_job_name(cls, v: str) -> str:
        """Validate job name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Job name must be non-empty")
        if len(v) > 100:
            raise ValueError("Job name must be at most 100 characters")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate extraction status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("extraction_type")
    @classmethod
    def validate_extraction_type(cls, v: str) -> str:
        """Validate extraction type"""
        if v not in cls.ALLOWED_EXTRACTION_TYPES:
            raise ValueError(f"Extraction type must be one of: {cls.ALLOWED_EXTRACTION_TYPES}")
        return v

    @field_validator("data_format")
    @classmethod
    def validate_data_format(cls, v: str) -> str:
        """Validate data format"""
        if v not in cls.ALLOWED_DATA_FORMATS:
            raise ValueError(f"Data format must be one of: {cls.ALLOWED_DATA_FORMATS}")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def start_extraction(self) -> None:
        """Mark extraction as started"""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def complete_extraction(self, records_extracted: int, records_processed: int) -> None:
        """Mark extraction as completed with results"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.records_extracted = records_extracted
        self.records_processed = records_processed
        self.last_successful_run = self.completed_at
        
        # Calculate duration
        if self.started_at:
            start_time = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
            self.duration_seconds = int((end_time - start_time).total_seconds())
        
        self.update_timestamp()

    def fail_extraction(self, error_message: str) -> None:
        """Mark extraction as failed with error details"""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.error_count += 1
        
        if self.error_messages is None:
            self.error_messages = []
        self.error_messages.append(error_message)
        
        self.update_timestamp()

    def should_retry(self) -> bool:
        """Check if extraction should be retried"""
        return self.retry_count < self.max_retries and self.status == "failed"

    def increment_retry(self) -> None:
        """Increment retry count and set status to retrying"""
        self.retry_count += 1
        self.status = "retrying"
        self.update_timestamp()

    def calculate_success_rate(self) -> float:
        """Calculate data processing success rate"""
        if self.records_extracted and self.records_extracted > 0:
            processed = self.records_processed or 0
            return (processed / self.records_extracted) * 100
        return 0.0

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["successRate"] = self.calculate_success_rate()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
