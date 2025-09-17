# entity/dataanalysis/version_1/dataanalysis.py

"""
DataAnalysis for Cyoda Client Application

Handles analysis of downloaded data using pandas and generates insights.
Represents analysis operations performed on data sources.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataAnalysis(CyodaEntity):
    """
    DataAnalysis represents an analysis operation on downloaded data.

    Manages data source references, analysis types, results, and metrics.
    The state field manages workflow states: initial_state -> pending -> analyzing -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataAnalysis"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    data_source_id: str = Field(
        ..., alias="dataSourceId", description="Reference to the DataSource entity"
    )
    analysis_type: str = Field(
        ...,
        alias="analysisType",
        description="Type of analysis (summary, statistical, trend)",
    )

    # Optional fields populated during processing
    results: Optional[Dict[str, Any]] = Field(
        default=None, description="Analysis results and insights"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Calculated metrics (mean, median, counts, etc.)"
    )
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="When analysis was performed (ISO 8601 format)",
    )

    # Validation rules
    ALLOWED_ANALYSIS_TYPES: ClassVar[list[str]] = ["summary", "statistical", "trend"]

    @field_validator("data_source_id")
    @classmethod
    def validate_data_source_id(cls, v: str) -> str:
        """Validate data_source_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Data source ID must be non-empty")
        return v.strip()

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, v: str) -> str:
        """Validate analysis_type field"""
        if v not in cls.ALLOWED_ANALYSIS_TYPES:
            raise ValueError(
                f"Analysis type must be one of: {cls.ALLOWED_ANALYSIS_TYPES}"
            )
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_analysis_results(
        self, results: Dict[str, Any], metrics: Dict[str, Any]
    ) -> None:
        """Set analysis results and metrics"""
        self.results = results
        self.metrics = metrics
        self.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def is_analysis_complete(self) -> bool:
        """Check if analysis is complete"""
        return self.results is not None and self.metrics is not None

    def is_ready_for_analysis(self) -> bool:
        """Check if entity is ready for analysis (in pending state)"""
        return self.state == "pending"

    def is_analyzing(self) -> bool:
        """Check if analysis is in progress"""
        return self.state == "analyzing"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
