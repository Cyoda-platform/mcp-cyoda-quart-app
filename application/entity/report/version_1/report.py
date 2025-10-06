# entity/report/version_1/report.py

"""
Report Entity for Booking Data Analysis

Represents generated reports summarizing booking data including total revenue,
average booking price, and number of bookings within specific date ranges
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class ReportSummary(BaseModel):
    """Summary statistics for the report"""

    total_bookings: int = Field(
        ..., alias="totalBookings", description="Total number of bookings"
    )
    total_revenue: float = Field(
        ..., alias="totalRevenue", description="Total revenue from all bookings"
    )
    average_booking_price: float = Field(
        ..., alias="averageBookingPrice", description="Average price per booking"
    )
    average_nights_per_booking: float = Field(
        ..., alias="averageNightsPerBooking", description="Average nights per booking"
    )
    deposit_paid_count: int = Field(
        ...,
        alias="depositPaidCount",
        description="Number of bookings with deposit paid",
    )
    deposit_paid_percentage: float = Field(
        ...,
        alias="depositPaidPercentage",
        description="Percentage of bookings with deposit paid",
    )


class DateRangeStats(BaseModel):
    """Statistics for a specific date range"""

    start_date: str = Field(
        ..., alias="startDate", description="Start date of the range"
    )
    end_date: str = Field(..., alias="endDate", description="End date of the range")
    booking_count: int = Field(
        ..., alias="bookingCount", description="Number of bookings in this range"
    )
    revenue: float = Field(..., description="Total revenue in this range")
    average_price: float = Field(
        ..., alias="averagePrice", description="Average booking price in this range"
    )


class Report(CyodaEntity):
    """
    Report entity represents generated reports summarizing booking data.

    Contains analysis of booking data including revenue calculations,
    booking counts, and statistics within specific date ranges for
    user-friendly display in tables or charts.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Report"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core report fields
    title: str = Field(..., description="Title of the report")
    description: Optional[str] = Field(
        default=None, description="Description of the report"
    )
    report_type: str = Field(
        ...,
        alias="reportType",
        description="Type of report (summary, filtered, date_range)",
    )

    # Report generation metadata
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="generatedAt",
        description="Timestamp when report was generated",
    )
    generated_by: str = Field(
        default="BookingReportProcessor",
        alias="generatedBy",
        description="System component that generated the report",
    )

    # Filter criteria used to generate the report
    filter_criteria: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="filterCriteria",
        description="Filter criteria used to generate this report",
    )

    # Report data and statistics
    summary: ReportSummary = Field(..., description="Summary statistics for the report")
    date_range_stats: Optional[List[DateRangeStats]] = Field(
        default=None,
        alias="dateRangeStats",
        description="Statistics broken down by date ranges",
    )

    # Raw data references
    booking_count: int = Field(
        ..., alias="bookingCount", description="Total number of bookings analyzed"
    )
    data_source: str = Field(
        default="Restful Booker API",
        alias="dataSource",
        description="Source of the booking data",
    )

    # Report format and display options
    display_format: str = Field(
        default="table",
        alias="displayFormat",
        description="Preferred display format (table, chart, json)",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is non-empty and reasonable length"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Report title must be non-empty")
        if len(v) > 200:
            raise ValueError("Report title must be at most 200 characters")
        return v.strip()

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type is one of allowed values"""
        allowed_types = ["summary", "filtered", "date_range", "custom"]
        if v not in allowed_types:
            raise ValueError(f"Report type must be one of: {allowed_types}")
        return v

    @field_validator("display_format")
    @classmethod
    def validate_display_format(cls, v: str) -> str:
        """Validate display format is one of allowed values"""
        allowed_formats = ["table", "chart", "json", "csv"]
        if v not in allowed_formats:
            raise ValueError(f"Display format must be one of: {allowed_formats}")
        return v

    @model_validator(mode="after")
    def validate_report_consistency(self) -> "Report":
        """Validate report data consistency"""
        if self.summary and self.booking_count != self.summary.total_bookings:
            raise ValueError("Booking count must match summary total bookings")

        if self.summary and self.summary.total_bookings > 0:
            if self.summary.average_booking_price <= 0:
                raise ValueError(
                    "Average booking price must be positive when bookings exist"
                )

        return self

    def add_date_range_stats(self, stats: DateRangeStats) -> None:
        """Add date range statistics to the report"""
        if self.date_range_stats is None:
            self.date_range_stats = []
        self.date_range_stats.append(stats)

    def get_revenue_by_deposit_status(self) -> Dict[str, float]:
        """Calculate revenue breakdown by deposit payment status"""
        if not self.summary:
            return {"deposit_paid": 0.0, "deposit_not_paid": 0.0}

        deposit_paid_revenue = self.summary.total_revenue * (
            self.summary.deposit_paid_percentage / 100
        )
        deposit_not_paid_revenue = self.summary.total_revenue - deposit_paid_revenue

        return {
            "deposit_paid": round(deposit_paid_revenue, 2),
            "deposit_not_paid": round(deposit_not_paid_revenue, 2),
        }

    def is_ready_for_display(self) -> bool:
        """Check if report is ready for display"""
        return (
            self.summary is not None
            and self.booking_count >= 0
            and self.state in ["generated", "completed"]
        )

    def to_display_format(self) -> Dict[str, Any]:
        """Convert report to user-friendly display format"""
        display_data: Dict[str, Any] = {
            "title": self.title,
            "description": self.description,
            "generated_at": self.generated_at,
            "summary": self.summary.model_dump(by_alias=True) if self.summary else None,
            "booking_count": self.booking_count,
            "revenue_by_deposit": self.get_revenue_by_deposit_status(),
        }

        if self.date_range_stats:
            display_data["date_ranges"] = [
                stats.model_dump(by_alias=True) for stats in self.date_range_stats
            ]

        if self.filter_criteria:
            display_data["filters_applied"] = self.filter_criteria

        return display_data

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
