# entity/data_extraction/version_1/data_extraction.py

"""
DataExtraction Entity for Pet Store Performance Analysis System

Represents a data extraction job that fetches product data from the Pet Store API
on a scheduled basis (every Monday) as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction entity represents a scheduled job that extracts product data
    from the Pet Store API for performance analysis.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> scheduled -> running -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Job identification and scheduling
    job_name: str = Field(
        ..., alias="jobName", description="Name of the data extraction job"
    )
    job_type: str = Field(
        default="WEEKLY_EXTRACTION",
        alias="jobType",
        description="Type of extraction job (WEEKLY_EXTRACTION, MANUAL_EXTRACTION, etc.)",
    )
    scheduled_time: str = Field(
        ...,
        alias="scheduledTime",
        description="Scheduled execution time (ISO 8601 format)",
    )
    cron_expression: Optional[str] = Field(
        default="0 9 * * MON",  # Every Monday at 9 AM
        alias="cronExpression",
        description="Cron expression for recurring jobs",
    )

    # Execution details
    started_at: Optional[str] = Field(
        default=None,
        alias="startedAt",
        description="Timestamp when the job started execution",
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when the job completed",
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        alias="durationSeconds",
        description="Job execution duration in seconds",
    )

    # API configuration
    api_base_url: str = Field(
        default="https://petstore3.swagger.io/api/v3",
        alias="apiBaseUrl",
        description="Base URL of the Pet Store API",
    )
    api_endpoints: List[str] = Field(
        default_factory=lambda: [
            "/pet/findByStatus?status=available",
            "/pet/findByStatus?status=pending",
            "/pet/findByStatus?status=sold",
        ],
        alias="apiEndpoints",
        description="List of API endpoints to extract data from",
    )
    api_key: Optional[str] = Field(
        default=None,
        alias="apiKey",
        description="API key for authentication (if required)",
    )

    # Extraction results
    total_records_extracted: int = Field(
        default=0,
        alias="totalRecordsExtracted",
        description="Total number of records extracted",
    )
    successful_extractions: int = Field(
        default=0,
        alias="successfulExtractions",
        description="Number of successful API calls",
    )
    failed_extractions: int = Field(
        default=0, alias="failedExtractions", description="Number of failed API calls"
    )
    extracted_data: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        alias="extractedData",
        description="Raw extracted data from the API",
    )

    # Status and error handling
    execution_status: str = Field(
        default="PENDING",
        alias="executionStatus",
        description="Current execution status (PENDING, RUNNING, COMPLETED, FAILED)",
    )
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if the job failed",
    )
    retry_count: int = Field(
        default=0, alias="retryCount", description="Number of retry attempts"
    )
    max_retries: int = Field(
        default=3, alias="maxRetries", description="Maximum number of retry attempts"
    )

    # Data processing flags
    create_products: bool = Field(
        default=True,
        alias="createProducts",
        description="Whether to create Product entities from extracted data",
    )
    update_existing: bool = Field(
        default=True,
        alias="updateExisting",
        description="Whether to update existing Product entities",
    )

    # Validation constants
    ALLOWED_JOB_TYPES: ClassVar[List[str]] = [
        "WEEKLY_EXTRACTION",
        "MANUAL_EXTRACTION",
        "DAILY_EXTRACTION",
        "MONTHLY_EXTRACTION",
    ]
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "PENDING",
        "RUNNING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    ]

    @field_validator("job_name")
    @classmethod
    def validate_job_name(cls, v: str) -> str:
        """Validate job name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Job name must be non-empty")
        if len(v) > 100:
            raise ValueError("Job name must be at most 100 characters long")
        return v.strip()

    @field_validator("job_type")
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        """Validate job type"""
        if v not in cls.ALLOWED_JOB_TYPES:
            raise ValueError(f"Job type must be one of: {cls.ALLOWED_JOB_TYPES}")
        return v

    @field_validator("execution_status")
    @classmethod
    def validate_execution_status(cls, v: str) -> str:
        """Validate execution status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Execution status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("api_base_url")
    @classmethod
    def validate_api_base_url(cls, v: str) -> str:
        """Validate API base URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("API base URL must start with http:// or https://")
        return v

    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(cls, v: int) -> int:
        """Validate retry count is not negative"""
        if v < 0:
            raise ValueError("Retry count cannot be negative")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is positive"""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "DataExtraction":
        """Validate business logic rules"""
        # If job is completed, it should have completion timestamp
        if self.execution_status == "COMPLETED" and not self.completed_at:
            raise ValueError("Completed jobs must have completion timestamp")

        # If job is running, it should have start timestamp
        if self.execution_status == "RUNNING" and not self.started_at:
            raise ValueError("Running jobs must have start timestamp")

        # Retry count should not exceed max retries
        if self.retry_count > self.max_retries:
            raise ValueError("Retry count cannot exceed max retries")

        # If there are failed extractions, there should be an error message
        if self.failed_extractions > 0 and not self.error_message:
            self.error_message = f"Job had {self.failed_extractions} failed extractions"

        return self

    def start_execution(self) -> None:
        """Mark the job as started"""
        self.execution_status = "RUNNING"
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def complete_execution(self) -> None:
        """Mark the job as completed"""
        self.execution_status = "COMPLETED"
        self.completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Calculate duration if we have start time
        if self.started_at:
            try:
                start_time = datetime.fromisoformat(
                    self.started_at.replace("Z", "+00:00")
                )
                end_time = datetime.fromisoformat(
                    self.completed_at.replace("Z", "+00:00")
                )
                self.duration_seconds = int((end_time - start_time).total_seconds())
            except ValueError:
                pass  # If timestamp parsing fails, leave duration as None

    def fail_execution(self, error_message: str) -> None:
        """Mark the job as failed"""
        self.execution_status = "FAILED"
        self.error_message = error_message
        self.completed_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def increment_retry(self) -> bool:
        """
        Increment retry count and check if more retries are allowed.

        Returns:
            True if more retries are allowed, False otherwise
        """
        self.retry_count += 1
        return self.retry_count <= self.max_retries

    def add_extracted_record(self, record: Dict[str, Any]) -> None:
        """Add a successfully extracted record"""
        if self.extracted_data is None:
            self.extracted_data = []
        self.extracted_data.append(record)
        self.total_records_extracted += 1

    def record_successful_extraction(self) -> None:
        """Record a successful API call"""
        self.successful_extractions += 1

    def record_failed_extraction(self, error: Optional[str] = None) -> None:
        """Record a failed API call"""
        self.failed_extractions += 1
        if error and not self.error_message:
            self.error_message = error

    def get_success_rate(self) -> float:
        """Calculate the success rate of API calls"""
        total_calls = self.successful_extractions + self.failed_extractions
        if total_calls == 0:
            return 0.0
        return (self.successful_extractions / total_calls) * 100

    def is_ready_for_retry(self) -> bool:
        """Check if the job is ready for retry"""
        return self.execution_status == "FAILED" and self.retry_count < self.max_retries

    def should_create_products(self) -> bool:
        """Check if Product entities should be created from extracted data"""
        return self.create_products and self.total_records_extracted > 0

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["success_rate"] = self.get_success_rate()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
