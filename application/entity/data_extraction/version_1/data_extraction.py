# entity/data_extraction/version_1/data_extraction.py

"""
DataExtraction Entity for Pet Store Performance Analysis System

Manages automated data collection from Pet Store API as specified in the
functional requirements for scheduled data extraction every Monday.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction represents a scheduled data collection job from Pet Store API.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> scheduled -> extracting -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Extraction job metadata
    job_name: str = Field(..., alias="jobName", description="Name of the extraction job")
    schedule_type: str = Field(
        default="weekly",
        alias="scheduleType",
        description="Schedule type (weekly, daily, monthly)"
    )
    target_day: str = Field(
        default="monday",
        alias="targetDay",
        description="Target day for extraction (monday, tuesday, etc.)"
    )
    
    # API configuration
    api_endpoint: str = Field(
        default="https://petstore.swagger.io/v2",
        alias="apiEndpoint",
        description="Pet Store API base endpoint"
    )
    data_format: str = Field(
        default="json",
        alias="dataFormat",
        description="Expected data format (json, xml)"
    )
    
    # Execution tracking
    last_execution: Optional[str] = Field(
        default=None,
        alias="lastExecution",
        description="Timestamp of last successful execution"
    )
    next_scheduled: Optional[str] = Field(
        default=None,
        alias="nextScheduled",
        description="Timestamp of next scheduled execution"
    )
    execution_status: str = Field(
        default="pending",
        alias="executionStatus",
        description="Current execution status"
    )
    
    # Extraction results
    products_extracted: Optional[int] = Field(
        default=0,
        alias="productsExtracted",
        description="Number of products extracted in last run"
    )
    extraction_errors: Optional[List[str]] = Field(
        default_factory=list,
        alias="extractionErrors",
        description="List of errors encountered during extraction"
    )
    extracted_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="extractedData",
        description="Raw extracted data from API"
    )
    
    # Processing metadata
    processed_products: Optional[int] = Field(
        default=0,
        alias="processedProducts",
        description="Number of products successfully processed"
    )
    failed_products: Optional[int] = Field(
        default=0,
        alias="failedProducts",
        description="Number of products that failed processing"
    )
    
    # Configuration options
    retry_count: int = Field(
        default=3,
        alias="retryCount",
        description="Number of retry attempts for failed extractions"
    )
    timeout_seconds: int = Field(
        default=300,
        alias="timeoutSeconds",
        description="Timeout for API calls in seconds"
    )

    # Validation constants
    ALLOWED_SCHEDULE_TYPES: ClassVar[List[str]] = [
        "daily", "weekly", "monthly"
    ]
    ALLOWED_DAYS: ClassVar[List[str]] = [
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ]
    ALLOWED_DATA_FORMATS: ClassVar[List[str]] = [
        "json", "xml"
    ]
    ALLOWED_EXECUTION_STATUSES: ClassVar[List[str]] = [
        "pending", "running", "completed", "failed", "cancelled"
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

    @field_validator("schedule_type")
    @classmethod
    def validate_schedule_type(cls, v: str) -> str:
        """Validate schedule type"""
        if v not in cls.ALLOWED_SCHEDULE_TYPES:
            raise ValueError(f"Schedule type must be one of: {cls.ALLOWED_SCHEDULE_TYPES}")
        return v

    @field_validator("target_day")
    @classmethod
    def validate_target_day(cls, v: str) -> str:
        """Validate target day"""
        if v not in cls.ALLOWED_DAYS:
            raise ValueError(f"Target day must be one of: {cls.ALLOWED_DAYS}")
        return v

    @field_validator("data_format")
    @classmethod
    def validate_data_format(cls, v: str) -> str:
        """Validate data format"""
        if v not in cls.ALLOWED_DATA_FORMATS:
            raise ValueError(f"Data format must be one of: {cls.ALLOWED_DATA_FORMATS}")
        return v

    @field_validator("execution_status")
    @classmethod
    def validate_execution_status(cls, v: str) -> str:
        """Validate execution status"""
        if v not in cls.ALLOWED_EXECUTION_STATUSES:
            raise ValueError(f"Execution status must be one of: {cls.ALLOWED_EXECUTION_STATUSES}")
        return v

    @field_validator("retry_count")
    @classmethod
    def validate_retry_count(cls, v: int) -> int:
        """Validate retry count"""
        if v < 0 or v > 10:
            raise ValueError("Retry count must be between 0 and 10")
        return v

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout_seconds(cls, v: int) -> int:
        """Validate timeout seconds"""
        if v < 30 or v > 3600:
            raise ValueError("Timeout must be between 30 and 3600 seconds")
        return v

    def mark_execution_start(self) -> None:
        """Mark the start of extraction execution"""
        self.execution_status = "running"
        self.last_execution = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_execution_complete(self, products_count: int) -> None:
        """Mark extraction as completed successfully"""
        self.execution_status = "completed"
        self.products_extracted = products_count
        self.processed_products = products_count

    def mark_execution_failed(self, error_message: str) -> None:
        """Mark extraction as failed with error"""
        self.execution_status = "failed"
        if self.extraction_errors is None:
            self.extraction_errors = []
        self.extraction_errors.append(error_message)

    def add_extraction_error(self, error: str) -> None:
        """Add an error to the extraction errors list"""
        if self.extraction_errors is None:
            self.extraction_errors = []
        self.extraction_errors.append(error)

    def calculate_success_rate(self) -> float:
        """Calculate the success rate of product processing"""
        total = (self.processed_products or 0) + (self.failed_products or 0)
        if total == 0:
            return 0.0
        return (self.processed_products or 0) / total * 100

    def is_due_for_execution(self) -> bool:
        """Check if extraction is due for execution"""
        if not self.next_scheduled:
            return True
        try:
            next_time = datetime.fromisoformat(self.next_scheduled.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) >= next_time
        except Exception:
            return True

    def schedule_next_execution(self) -> None:
        """Schedule the next execution based on schedule type"""
        now = datetime.now(timezone.utc)
        if self.schedule_type == "weekly":
            # Schedule for next Monday (or today if it's Monday and hasn't run)
            days_ahead = 7 - now.weekday()  # Monday is 0
            if days_ahead == 7:  # Today is Monday
                days_ahead = 0 if not self.last_execution else 7
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
            next_run = next_run.replace(day=now.day + days_ahead)
        else:
            # Default to next day for other schedule types
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
            next_run = next_run.replace(day=now.day + 1)
        
        self.next_scheduled = next_run.isoformat().replace("+00:00", "Z")

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
