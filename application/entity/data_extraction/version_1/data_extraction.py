# entity/data_extraction/version_1/data_extraction.py

"""
DataExtraction Entity for Pet Store Performance Analysis System

Represents automated data collection processes from the Pet Store API,
tracking extraction status, schedules, and data quality as specified
in functional requirements for Monday data extraction automation.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataExtraction(CyodaEntity):
    """
    DataExtraction represents an automated data collection process from the Pet Store API,
    tracking extraction schedules, status, and data quality for performance analysis.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> scheduled -> extracting -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataExtraction"
    ENTITY_VERSION: ClassVar[int] = 1

    # Extraction identification and scheduling
    extraction_name: str = Field(
        ..., description="Name/identifier for this extraction process"
    )
    extraction_type: str = Field(
        default="WEEKLY",
        alias="extractionType",
        description="Type of extraction: WEEKLY, DAILY, MONTHLY",
    )
    scheduled_day: str = Field(
        default="MONDAY",
        alias="scheduledDay",
        description="Day of week for scheduled extraction",
    )
    scheduled_time: str = Field(
        default="09:00",
        alias="scheduledTime",
        description="Time of day for extraction (HH:MM format)",
    )

    # API configuration
    api_endpoint: str = Field(
        default="https://petstore.swagger.io/v2",
        alias="apiEndpoint",
        description="Base URL for Pet Store API",
    )
    api_format: str = Field(
        default="JSON",
        alias="apiFormat",
        description="Data format for API requests: JSON, XML",
    )

    # Extraction execution details
    last_execution_at: Optional[str] = Field(
        default=None,
        alias="lastExecutionAt",
        description="Timestamp of last extraction execution",
    )
    next_execution_at: Optional[str] = Field(
        default=None,
        alias="nextExecutionAt",
        description="Timestamp of next scheduled extraction",
    )
    execution_status: str = Field(
        default="PENDING",
        alias="executionStatus",
        description="Current execution status",
    )

    # Data extraction results
    products_extracted: Optional[int] = Field(
        default=0,
        alias="productsExtracted",
        description="Number of products successfully extracted",
    )
    extraction_duration_ms: Optional[int] = Field(
        default=None,
        alias="extractionDurationMs",
        description="Duration of extraction process in milliseconds",
    )
    data_quality_score: Optional[float] = Field(
        default=None,
        alias="dataQualityScore",
        description="Data quality score (0-100) based on completeness and validity",
    )

    # Error handling and monitoring
    error_count: Optional[int] = Field(
        default=0,
        alias="errorCount",
        description="Number of errors encountered during extraction",
    )
    last_error_message: Optional[str] = Field(
        default=None,
        alias="lastErrorMessage",
        description="Last error message if extraction failed",
    )
    retry_count: Optional[int] = Field(
        default=0, alias="retryCount", description="Number of retry attempts made"
    )

    # Extracted data summary
    extraction_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="extractionSummary",
        description="Summary of extracted data including categories and counts",
    )
    extracted_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        alias="extractedData",
        description="Raw extracted data from Pet Store API",
    )

    # Processing metadata
    processed_by: Optional[str] = Field(
        default="DataExtractionProcessor",
        alias="processedBy",
        description="System component that processed the extraction",
    )

    # Validation constants
    ALLOWED_EXTRACTION_TYPES: ClassVar[List[str]] = [
        "DAILY",
        "WEEKLY",
        "MONTHLY",
        "ON_DEMAND",
    ]
    ALLOWED_DAYS: ClassVar[List[str]] = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]
    ALLOWED_FORMATS: ClassVar[List[str]] = ["JSON", "XML"]
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "PENDING",
        "SCHEDULED",
        "RUNNING",
        "COMPLETED",
        "FAILED",
        "RETRY",
    ]

    @field_validator("extraction_name")
    @classmethod
    def validate_extraction_name(cls, v: str) -> str:
        """Validate extraction name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Extraction name must be non-empty")
        if len(v) > 100:
            raise ValueError("Extraction name must be at most 100 characters")
        return v.strip()

    @field_validator("extraction_type")
    @classmethod
    def validate_extraction_type(cls, v: str) -> str:
        """Validate extraction type"""
        if v not in cls.ALLOWED_EXTRACTION_TYPES:
            raise ValueError(
                f"Extraction type must be one of: {cls.ALLOWED_EXTRACTION_TYPES}"
            )
        return v

    @field_validator("scheduled_day")
    @classmethod
    def validate_scheduled_day(cls, v: str) -> str:
        """Validate scheduled day"""
        if v not in cls.ALLOWED_DAYS:
            raise ValueError(f"Scheduled day must be one of: {cls.ALLOWED_DAYS}")
        return v

    @field_validator("api_format")
    @classmethod
    def validate_api_format(cls, v: str) -> str:
        """Validate API format"""
        if v not in cls.ALLOWED_FORMATS:
            raise ValueError(f"API format must be one of: {cls.ALLOWED_FORMATS}")
        return v

    @field_validator("execution_status")
    @classmethod
    def validate_execution_status(cls, v: str) -> str:
        """Validate execution status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Execution status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    def update_execution_timestamp(self) -> None:
        """Update the last execution timestamp to current time"""
        self.last_execution_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

    def mark_extraction_started(self) -> None:
        """Mark extraction as started"""
        self.execution_status = "RUNNING"
        self.update_execution_timestamp()

    def mark_extraction_completed(self, products_count: int, duration_ms: int) -> None:
        """Mark extraction as completed with results"""
        self.execution_status = "COMPLETED"
        self.products_extracted = products_count
        self.extraction_duration_ms = duration_ms
        self.error_count = 0
        self.last_error_message = None

    def mark_extraction_failed(self, error_message: str) -> None:
        """Mark extraction as failed with error message"""
        self.execution_status = "FAILED"
        self.last_error_message = error_message
        self.error_count = (self.error_count or 0) + 1

    def increment_retry_count(self) -> None:
        """Increment retry count for failed extractions"""
        self.retry_count = (self.retry_count or 0) + 1
        self.execution_status = "RETRY"

    def set_extracted_data(self, data: List[Dict[str, Any]]) -> None:
        """Set extracted data and update summary"""
        self.extracted_data = data
        self.products_extracted = len(data)

        # Generate extraction summary
        categories = {}
        for item in data:
            category = item.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        self.extraction_summary = {
            "total_products": len(data),
            "categories": categories,
            "extraction_timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    def calculate_data_quality_score(self) -> float:
        """Calculate data quality score based on completeness"""
        if not self.extracted_data:
            self.data_quality_score = 0.0
            return 0.0

        total_fields = 0
        complete_fields = 0
        required_fields = ["id", "name", "category", "status"]

        for item in self.extracted_data:
            for field in required_fields:
                total_fields += 1
                if field in item and item[field] is not None:
                    complete_fields += 1

        if total_fields > 0:
            self.data_quality_score = (complete_fields / total_fields) * 100
        else:
            self.data_quality_score = 0.0

        return self.data_quality_score

    def is_ready_for_processing(self) -> bool:
        """Check if extraction is ready for data processing"""
        return (
            self.execution_status == "COMPLETED"
            and self.extracted_data is not None
            and len(self.extracted_data) > 0
        )

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
