# entity/comment/version_1/comment.py

"""
Comment Entity for Cyoda Client Application

Represents comment data ingested from external APIs for analysis and reporting.
Stores comment content, metadata, and ingestion information as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Comment(CyodaEntity):
    """
    Comment entity represents comment data ingested from external APIs.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> ingested -> validated -> analysis_triggered -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Comment"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    source_api: str = Field(..., description="API source where the comment was retrieved from")
    external_id: str = Field(..., description="Original comment ID from the external API")
    content: str = Field(..., description="The actual comment text content")
    author: str = Field(..., description="Comment author information")
    timestamp: str = Field(..., description="When the comment was created (ISO 8601 format)")
    
    # Optional fields
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional data from the API (likes, replies, etc.)"
    )
    ingested_at: Optional[str] = Field(
        default=None,
        description="When the comment was ingested into the system (ISO 8601 format)"
    )

    # Processing-related fields (populated during processing)
    validation_status: Optional[str] = Field(
        default=None,
        description="Status of validation checks"
    )
    analysis_triggered: Optional[bool] = Field(
        default=False,
        description="Flag indicating if analysis has been triggered"
    )

    @field_validator("source_api")
    @classmethod
    def validate_source_api(cls, v: str) -> str:
        """Validate source_api field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Source API must be non-empty")
        if len(v) > 50:
            raise ValueError("Source API must be at most 50 characters long")
        return v.strip()

    @field_validator("external_id")
    @classmethod
    def validate_external_id(cls, v: str) -> str:
        """Validate external_id field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("External ID must be non-empty")
        if len(v) > 100:
            raise ValueError("External ID must be at most 100 characters long")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Comment content must be non-empty")
        if len(v) > 10000:
            raise ValueError("Comment content must be at most 10000 characters long")
        return v.strip()

    @field_validator("author")
    @classmethod
    def validate_author(cls, v: str) -> str:
        """Validate author field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Comment author must be non-empty")
        if len(v) > 100:
            raise ValueError("Comment author must be at most 100 characters long")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp field (ISO 8601 format)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Timestamp must be non-empty")
        try:
            # Try to parse the timestamp to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Timestamp must be in ISO 8601 format")
        return v.strip()

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Comment":
        """Validate business logic rules"""
        # Ensure metadata is a dictionary
        if self.metadata is not None and not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        return self

    def set_ingested_at(self) -> None:
        """Set the ingested_at timestamp to current time"""
        self.ingested_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_validation_status(self, status: str) -> None:
        """Set validation status and update timestamp"""
        self.validation_status = status
        self.update_timestamp()

    def set_analysis_triggered(self, triggered: bool = True) -> None:
        """Set analysis triggered flag and update timestamp"""
        self.analysis_triggered = triggered
        self.update_timestamp()

    def is_ready_for_validation(self) -> bool:
        """Check if comment is ready for validation (in ingested state)"""
        return self.state == "ingested"

    def is_validated(self) -> bool:
        """Check if comment has been validated"""
        return self.state == "validated"

    def is_analysis_triggered(self) -> bool:
        """Check if analysis has been triggered"""
        return self.state == "analysis_triggered" or self.analysis_triggered is True

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
