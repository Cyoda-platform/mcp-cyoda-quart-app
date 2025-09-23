"""
Report Entity for Product Performance Analysis and Reporting System

Represents performance analysis reports that are generated and emailed to stakeholders.
Extends CyodaEntity to integrate with Cyoda workflow system.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Report(CyodaEntity):
    """
    Report entity representing performance analysis reports.
    
    This entity stores report data that gets generated from Pet Store API analysis
    and is used for emailing weekly reports to stakeholders.
    
    Inherits from CyodaEntity to get workflow management capabilities.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Report identification
    report_title: str = Field(
        ...,
        alias="reportTitle",
        description="Title of the report"
    )
    report_type: str = Field(
        ...,
        alias="reportType",
        description="Type of report (weekly, monthly, custom)"
    )
    report_period: str = Field(
        ...,
        alias="reportPeriod",
        description="Period covered by the report (e.g., '2024-01-01 to 2024-01-07')"
    )

    # Report content
    report_data: Dict[str, Any] = Field(
        default_factory=dict,
        alias="reportData",
        description="Report data including metrics, charts, and analysis"
    )
    summary: Optional[str] = Field(
        None,
        description="Executive summary of the report"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of recommendations based on analysis"
    )

    # Generation metadata
    generated_at: Optional[str] = Field(
        None,
        alias="generatedAt",
        description="Timestamp when report was generated"
    )
    generated_by: Optional[str] = Field(
        None,
        alias="generatedBy",
        description="System or user that generated the report"
    )
    data_source: Optional[str] = Field(
        None,
        alias="dataSource",
        description="Source of data used for the report"
    )

    # Email delivery
    email_recipient: str = Field(
        ...,
        alias="emailRecipient",
        description="Email address to send the report to"
    )
    email_subject: Optional[str] = Field(
        None,
        alias="emailSubject",
        description="Email subject line"
    )
    email_sent_at: Optional[str] = Field(
        None,
        alias="emailSentAt",
        description="Timestamp when email was sent"
    )
    email_status: Optional[str] = Field(
        None,
        alias="emailStatus",
        description="Status of email delivery (pending, sent, failed)"
    )

    # Report metrics
    total_pets_analyzed: Optional[int] = Field(
        None,
        alias="totalPetsAnalyzed",
        description="Total number of pets included in analysis"
    )
    stores_analyzed: Optional[int] = Field(
        None,
        alias="storesAnalyzed",
        description="Number of stores included in analysis"
    )
    performance_score: Optional[float] = Field(
        None,
        alias="performanceScore",
        description="Overall performance score for the period"
    )

    # Validation constants
    VALID_REPORT_TYPES: ClassVar[List[str]] = ["weekly", "monthly", "quarterly", "custom"]
    VALID_EMAIL_STATUSES: ClassVar[List[str]] = ["pending", "sent", "failed", "scheduled"]

    @field_validator("report_title")
    @classmethod
    def validate_report_title(cls, v: str) -> str:
        """Validate report title"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 255:
            raise ValueError("Report title must be at most 255 characters")
        return v.strip()

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type"""
        if v not in cls.VALID_REPORT_TYPES:
            raise ValueError(f"Report type must be one of: {cls.VALID_REPORT_TYPES}")
        return v

    @field_validator("email_recipient")
    @classmethod
    def validate_email_recipient(cls, v: str) -> str:
        """Validate email recipient"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Email recipient must be non-empty")
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.strip().lower()

    @field_validator("email_status")
    @classmethod
    def validate_email_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate email status"""
        if v is not None and v not in cls.VALID_EMAIL_STATUSES:
            raise ValueError(f"Email status must be one of: {cls.VALID_EMAIL_STATUSES}")
        return v

    @field_validator("performance_score")
    @classmethod
    def validate_performance_score(cls, v: Optional[float]) -> Optional[float]:
        """Validate performance score"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("Performance score must be between 0.0 and 100.0")
        return v

    def generate_report(self, data: Dict[str, Any], generated_by: str = "System") -> None:
        """Generate report with provided data"""
        self.report_data = data
        self.generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.generated_by = generated_by
        self.email_status = "pending"
        self.update_timestamp()

    def mark_email_sent(self) -> None:
        """Mark report as successfully emailed"""
        self.email_sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.email_status = "sent"
        self.update_timestamp()

    def mark_email_failed(self) -> None:
        """Mark report email as failed"""
        self.email_status = "failed"
        self.update_timestamp()

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the report"""
        if recommendation and recommendation.strip():
            self.recommendations.append(recommendation.strip())
            self.update_timestamp()

    def set_performance_metrics(self, total_pets: int, stores: int, score: float) -> None:
        """Set performance metrics for the report"""
        self.total_pets_analyzed = total_pets
        self.stores_analyzed = stores
        self.performance_score = score
        self.update_timestamp()

    def is_generated(self) -> bool:
        """Check if report has been generated"""
        return self.generated_at is not None and bool(self.report_data)

    def is_email_sent(self) -> bool:
        """Check if report has been emailed"""
        return self.email_status == "sent" and self.email_sent_at is not None

    def get_email_subject_line(self) -> str:
        """Generate email subject line if not set"""
        if self.email_subject:
            return self.email_subject
        return f"{self.report_title} - {self.report_period}"

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
