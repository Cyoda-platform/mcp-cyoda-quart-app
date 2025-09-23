"""
DataExtraction Entity for Product Performance Analysis and Reporting System

Represents data extraction jobs from the Pet Store API including
scheduling information, execution status, and extraction results.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction entity represents data extraction jobs from Pet Store API.
    
    Manages scheduling, execution status, and results of automated data
    extraction processes for product performance analysis.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core extraction fields
    extraction_type: str = Field(
        default="pet_store_products",
        alias="extractionType",
        description="Type of data extraction (pet_store_products, inventory_update, etc.)"
    )
    source_url: str = Field(
        default="https://petstore.swagger.io/v2",
        alias="sourceUrl",
        description="Source API URL for data extraction"
    )
    
    # Scheduling information
    scheduled_for: Optional[str] = Field(
        default=None,
        alias="scheduledFor",
        description="Timestamp when extraction is scheduled to run"
    )
    schedule_pattern: Optional[str] = Field(
        default="weekly_monday",
        alias="schedulePattern",
        description="Schedule pattern (weekly_monday, daily, monthly, etc.)"
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
    duration_seconds: Optional[float] = Field(
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
    records_failed: Optional[int] = Field(
        default=None,
        alias="recordsFailed",
        description="Number of records that failed to extract"
    )
    products_created: Optional[int] = Field(
        default=None,
        alias="productsCreated",
        description="Number of new Product entities created"
    )
    products_updated: Optional[int] = Field(
        default=None,
        alias="productsUpdated",
        description="Number of existing Product entities updated"
    )
    
    # Error tracking
    error_message: Optional[str] = Field(
        default=None,
        alias="errorMessage",
        description="Error message if extraction failed"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="errorDetails",
        description="Detailed error information"
    )
    
    # API interaction details
    api_endpoints_called: Optional[List[str]] = Field(
        default_factory=list,
        alias="apiEndpointsCalled",
        description="List of API endpoints that were called"
    )
    api_response_codes: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        alias="apiResponseCodes",
        description="HTTP response codes from API calls"
    )
    
    # Data quality metrics
    data_quality_score: Optional[float] = Field(
        default=None,
        alias="dataQualityScore",
        description="Data quality score (0-100)"
    )
    validation_errors: Optional[List[str]] = Field(
        default_factory=list,
        alias="validationErrors",
        description="List of data validation errors encountered"
    )
    
    # Configuration
    extraction_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="extractionConfig",
        description="Configuration parameters for the extraction"
    )
    retry_count: Optional[int] = Field(
        default=0,
        alias="retryCount",
        description="Number of retry attempts"
    )
    max_retries: Optional[int] = Field(
        default=3,
        alias="maxRetries",
        description="Maximum number of retry attempts"
    )

    # Validation constants
    ALLOWED_EXTRACTION_TYPES: ClassVar[List[str]] = [
        "pet_store_products", "inventory_update", "price_update", "full_sync"
    ]
    ALLOWED_SCHEDULE_PATTERNS: ClassVar[List[str]] = [
        "weekly_monday", "daily", "weekly", "monthly", "manual"
    ]

    @field_validator("extraction_type")
    @classmethod
    def validate_extraction_type(cls, v: str) -> str:
        """Validate extraction type"""
        if v not in cls.ALLOWED_EXTRACTION_TYPES:
            raise ValueError(f"Extraction type must be one of: {cls.ALLOWED_EXTRACTION_TYPES}")
        return v

    @field_validator("schedule_pattern")
    @classmethod
    def validate_schedule_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate schedule pattern"""
        if v is not None and v not in cls.ALLOWED_SCHEDULE_PATTERNS:
            raise ValueError(f"Schedule pattern must be one of: {cls.ALLOWED_SCHEDULE_PATTERNS}")
        return v

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str) -> str:
        """Validate source URL"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Source URL must be a valid HTTP/HTTPS URL")
        return v

    def mark_started(self) -> None:
        """Mark extraction as started"""
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def mark_completed(self, success: bool = True) -> None:
        """Mark extraction as completed"""
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Calculate duration if started_at is available
        if self.started_at:
            try:
                start_time = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
                end_time = datetime.now(timezone.utc)
                self.duration_seconds = (end_time - start_time).total_seconds()
            except Exception:
                pass  # Ignore duration calculation errors
        
        self.update_timestamp()

    def add_error(self, error_message: str, error_details: Optional[Dict[str, Any]] = None) -> None:
        """Add error information to the extraction"""
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
        self.update_timestamp()

    def increment_retry(self) -> bool:
        """Increment retry count and return True if more retries allowed"""
        if self.retry_count is None:
            self.retry_count = 0
        
        self.retry_count += 1
        self.update_timestamp()
        
        return self.retry_count < (self.max_retries or 3)

    def add_api_call(self, endpoint: str, response_code: int) -> None:
        """Record an API call and its response code"""
        if self.api_endpoints_called is None:
            self.api_endpoints_called = []
        if self.api_response_codes is None:
            self.api_response_codes = {}
        
        self.api_endpoints_called.append(endpoint)
        self.api_response_codes[endpoint] = response_code
        self.update_timestamp()

    def calculate_success_rate(self) -> float:
        """Calculate extraction success rate"""
        total_records = (self.records_extracted or 0) + (self.records_failed or 0)
        if total_records == 0:
            return 0.0
        
        return (self.records_extracted or 0) / total_records * 100

    def is_scheduled_for_today(self) -> bool:
        """Check if extraction is scheduled for today"""
        if not self.scheduled_for:
            return False
        
        try:
            scheduled_date = datetime.fromisoformat(self.scheduled_for.replace("Z", "+00:00"))
            today = datetime.now(timezone.utc).date()
            return scheduled_date.date() == today
        except Exception:
            return False

    def should_retry(self) -> bool:
        """Check if extraction should be retried"""
        return (
            self.error_message is not None 
            and (self.retry_count or 0) < (self.max_retries or 3)
            and self.state in ["failed", "error"]
        )

    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction results"""
        return {
            "extraction_type": self.extraction_type,
            "success_rate": self.calculate_success_rate(),
            "records_extracted": self.records_extracted or 0,
            "records_failed": self.records_failed or 0,
            "products_created": self.products_created or 0,
            "products_updated": self.products_updated or 0,
            "duration_seconds": self.duration_seconds,
            "retry_count": self.retry_count or 0,
            "has_errors": self.error_message is not None
        }

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
