# entity/datasource/version_1/datasource.py

"""
DataSource for Cyoda Client Application

Manages external data sources and handles downloading data from URLs.
Represents data sources that can be downloaded and processed for analysis.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class DataSource(CyodaEntity):
    """
    DataSource represents an external data source that can be downloaded.
    
    Manages URLs, data formats, download status, and file information.
    The state field manages workflow states: initial_state -> pending -> downloading -> completed/failed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "DataSource"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    url: str = Field(..., description="The URL to download data from")
    data_format: str = Field(..., description="Format of the data (csv, json, xml)")
    
    # Optional fields populated during processing
    last_downloaded: Optional[str] = Field(
        default=None,
        alias="lastDownloaded",
        description="Timestamp of last successful download (ISO 8601 format)",
    )
    file_size: Optional[int] = Field(
        default=None,
        alias="fileSize",
        description="Size of downloaded file in bytes",
    )
    status: str = Field(
        default="pending",
        description="Current status (pending, downloading, completed, failed)",
    )

    # Validation rules
    ALLOWED_FORMATS: ClassVar[list[str]] = ["csv", "json", "xml"]
    ALLOWED_STATUSES: ClassVar[list[str]] = ["pending", "downloading", "completed", "failed"]

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("URL must be non-empty")
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.strip()

    @field_validator("data_format")
    @classmethod
    def validate_data_format(cls, v: str) -> str:
        """Validate data_format field"""
        if v not in cls.ALLOWED_FORMATS:
            raise ValueError(f"Data format must be one of: {cls.ALLOWED_FORMATS}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status field"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate file_size field"""
        if v is not None and v < 0:
            raise ValueError("File size must be non-negative")
        return v

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_download_completed(self, file_size: int) -> None:
        """Mark download as completed with file size"""
        self.status = "completed"
        self.file_size = file_size
        self.last_downloaded = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def set_download_failed(self) -> None:
        """Mark download as failed"""
        self.status = "failed"
        self.update_timestamp()

    def set_downloading(self) -> None:
        """Mark download as in progress"""
        self.status = "downloading"
        self.update_timestamp()

    def is_download_completed(self) -> bool:
        """Check if download is completed"""
        return self.status == "completed"

    def is_download_failed(self) -> bool:
        """Check if download failed"""
        return self.status == "failed"

    def is_downloading(self) -> bool:
        """Check if download is in progress"""
        return self.status == "downloading"

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
