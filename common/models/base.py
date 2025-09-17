"""
Base Models and Validation.

This module provides base Pydantic models for data validation and serialization
with comprehensive validation rules and error handling.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

# The logging module lacks type stubs in your repo; ignore that for mypy.
from common.observability.logging import get_logger  # type: ignore[import-untyped]

logger = get_logger(__name__)

# ======================================================================================
# Enums
# ======================================================================================


class ValidationSeverity(Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EntityType(Enum):
    """Supported entity types."""

    EDGE_MESSAGE = "EDGE_MESSAGE"
    CHAT_MESSAGE = "CHAT_MESSAGE"
    USER = "USER"
    SESSION = "SESSION"
    WORKFLOW = "WORKFLOW"
    PROCESSOR = "PROCESSOR"
    CRITERIA = "CRITERIA"


class ProcessingStatus(Enum):
    """Processing status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ======================================================================================
# Base model
# ======================================================================================

TBaseModel = TypeVar("TBaseModel", bound="BaseValidatedModel")


class BaseValidatedModel(BaseModel):
    """Base model with enhanced validation and serialization."""

    model_config = ConfigDict(
        # Allow extra fields for flexibility
        extra="allow",
        # Use enum values instead of names
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
        # Allow population by field name or alias
        populate_by_name=True,
        # JSON encoders for custom types
        ser_json_timedelta="iso8601",
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
        },
        # Schema extra information
        json_schema_extra={"example": {}},
    )

    def dict_safe(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary with safe serialization."""
        try:
            return self.model_dump(**kwargs)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to serialize model: {e}")
            return {
                "error": "serialization_failed",
                "type": self.__class__.__name__,
            }

    def json_safe(self, **kwargs: Any) -> str:
        """Convert to JSON with safe serialization."""
        try:
            return self.model_dump_json(**kwargs)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to serialize model to JSON: {e}")
            return '{"error": "json_serialization_failed"}'

    @classmethod
    def validate_data(cls: Type[TBaseModel], data: Dict[str, Any]) -> TBaseModel:
        """Validate data and return model instance."""
        try:
            return cls(**data)
        except ValidationError as e:
            logger.error(f"Validation failed for {cls.__name__}: {e}")
            raise

    @classmethod
    def from_dict_safe(
        cls: Type[TBaseModel], data: Dict[str, Any]
    ) -> Optional[TBaseModel]:
        """Create instance from dictionary with error handling."""
        try:
            return cls(**data)
        except ValidationError as e:
            logger.warning(f"Failed to create {cls.__name__} from dict: {e}")
            return None
        except Exception as e:  # noqa: BLE001
            logger.error(f"Unexpected error creating {cls.__name__}: {e}")
            return None


# ======================================================================================
# Concrete models
# ======================================================================================


class EntityMetadata(BaseValidatedModel):
    """Entity metadata model."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = Field(
        default=None, description="User who created the entity"
    )
    updated_by: Optional[str] = Field(
        default=None, description="User who last updated the entity"
    )
    version: int = Field(default=1, ge=1, description="Entity version number")
    tags: List[str] = Field(default_factory=list, description="Entity tags")
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata fields"
    )

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Parse datetime from various formats."""
        if isinstance(v, str):
            # Handle ISO format with Z suffix
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return datetime.fromisoformat(v)
        if isinstance(v, datetime):
            return v
        raise TypeError("Invalid datetime value")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags format."""
        if not isinstance(v, list):
            return []
        validated_tags: List[str] = []
        for tag in v:
            if isinstance(tag, str) and re.match(r"^[a-zA-Z0-9_-]+$", tag):
                validated_tags.append(tag.lower())
        return validated_tags


class EntityId(BaseValidatedModel):
    """Entity identifier model."""

    entity_id: str = Field(
        ...,
        description="Unique entity identifier",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    entity_type: EntityType = Field(..., description="Type of entity")

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity ID format."""
        if not v or not isinstance(v, str):
            raise ValueError("Entity ID must be a non-empty string")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Entity ID contains invalid characters")
        return v.strip()


class ProcessorRequest(BaseValidatedModel):
    """Processor request model."""

    processor_name: str = Field(
        ...,
        description="Name of the processor to execute",
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    entity_id: str = Field(
        ..., description="ID of the entity to process", min_length=1, max_length=100
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique request ID"
    )
    correlation_id: Optional[str] = Field(
        default=None, description="Correlation ID for tracing"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Processor parameters"
    )
    timeout_seconds: float = Field(
        default=30.0, description="Processing timeout", gt=0, le=300
    )
    priority: int = Field(default=5, description="Processing priority", ge=1, le=10)

    @field_validator("processor_name")
    @classmethod
    def validate_processor_name(cls, v: str) -> str:
        """Validate processor name format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Processor name contains invalid characters")
        return v.lower()

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processor parameters."""
        if not isinstance(v, dict):
            return {}
        validated_params: Dict[str, Any] = {}
        for key, value in v.items():
            if isinstance(key, str) and len(key) <= 50:
                validated_params[key] = value
        return validated_params


class ProcessorResponse(BaseValidatedModel):
    """Processor response model."""

    request_id: str = Field(..., description="Original request ID")
    processor_name: str = Field(..., description="Name of the processor that executed")
    entity_id: str = Field(..., description="ID of the processed entity")
    status: ProcessingStatus = Field(..., description="Processing status")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Processing result"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds", ge=0
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )

    @field_validator("status")  # type: ignore[type-var]
    @classmethod
    def validate_status_consistency(
        cls, v: ProcessingStatus, values: Dict[str, Any]
    ) -> ProcessingStatus:
        """Validate status consistency with other fields."""
        error_message = values.get("error_message")
        if v == ProcessingStatus.FAILED:
            if not error_message:
                raise ValueError("Error message required for failed status")
        elif v == ProcessingStatus.COMPLETED:
            if error_message:
                raise ValueError("Error message not allowed for completed status")
        return v


class CriteriaRequest(BaseValidatedModel):
    """Criteria check request model."""

    criteria_name: str = Field(
        ...,
        description="Name of the criteria to check",
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    entity_id: str = Field(
        ..., description="ID of the entity to check", min_length=1, max_length=100
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique request ID"
    )
    correlation_id: Optional[str] = Field(
        default=None, description="Correlation ID for tracing"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Criteria parameters"
    )

    @field_validator("criteria_name")
    @classmethod
    def validate_criteria_name(cls, v: str) -> str:
        """Validate criteria name format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Criteria name contains invalid characters")
        return v.lower()


class CriteriaResponse(BaseValidatedModel):
    """Criteria check response model."""

    request_id: str = Field(..., description="Original request ID")
    criteria_name: str = Field(..., description="Name of the criteria that was checked")
    entity_id: str = Field(..., description="ID of the checked entity")
    matches: bool = Field(..., description="Whether the entity matches the criteria")
    confidence: float = Field(
        default=1.0, description="Confidence score", ge=0.0, le=1.0
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Detailed check results"
    )
    processing_time_ms: float = Field(
        ..., description="Check time in milliseconds", ge=0
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )


class HealthCheckResult(BaseValidatedModel):
    """Health check result model."""

    check_name: str = Field(..., description="Name of the health check")
    status: str = Field(..., description="Health check status")
    message: str = Field(default="", description="Health check message")
    duration_ms: float = Field(..., description="Check duration in milliseconds", ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Detailed check information"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate health check status."""
        valid_statuses = {"healthy", "degraded", "unhealthy", "unknown"}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {sorted(valid_statuses)}")
        return v.lower()


class ConfigurationModel(BaseValidatedModel):
    """Configuration model with validation."""

    section: str = Field(
        ..., description="Configuration section name", pattern=r"^[a-zA-Z0-9._-]+$"
    )
    key: str = Field(..., description="Configuration key", pattern=r"^[a-zA-Z0-9._-]+$")
    value: Any = Field(..., description="Configuration value")
    data_type: str = Field(..., description="Value data type")
    description: Optional[str] = Field(
        default=None, description="Configuration description"
    )
    required: bool = Field(
        default=False, description="Whether the configuration is required"
    )
    sensitive: bool = Field(
        default=False,
        description="Whether the configuration contains sensitive data",
    )

    @field_validator("section", "key")
    @classmethod
    def validate_identifiers(cls, v: str) -> str:
        """Validate configuration identifiers."""
        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError("Invalid identifier format")
        return v.lower()

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        """Validate data type."""
        valid_types = {"string", "integer", "float", "boolean", "list", "dict"}
        if v.lower() not in valid_types:
            raise ValueError(f"Data type must be one of: {sorted(valid_types)}")
        return v.lower()


# ======================================================================================
# Public helpers
# ======================================================================================


def validate_model_data(
    model_class: Type[TBaseModel], data: Dict[str, Any]
) -> TBaseModel:
    """Validate data against a model class."""
    try:
        return model_class.validate_data(data)
    except ValidationError as e:
        logger.error(f"Validation failed for {model_class.__name__}: {e}")
        raise


def is_pydantic_available() -> bool:
    """Check if Pydantic is available."""
    # This module requires Pydantic; always True.
    return True


# Constant for backward compatibility
PYDANTIC_AVAILABLE = True


# ======================================================================================
# Validation utilities
# ======================================================================================


class ValidationUtils:
    """Utility functions for data validation."""

    @staticmethod
    def validate_entity_id(entity_id: str) -> bool:
        """Validate entity ID format."""
        if not entity_id or not isinstance(entity_id, str):
            return False
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", entity_id.strip()))

    @staticmethod
    def validate_processor_name(processor_name: str) -> bool:
        """Validate processor name format."""
        if not processor_name or not isinstance(processor_name, str):
            return False
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", processor_name.strip()))

    @staticmethod
    def sanitize_string(value: Any, max_length: int = 255) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            return str(value)[:max_length]
        return value.strip()[:max_length]

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        if not uuid_str or not isinstance(uuid_str, str):
            return False
        try:
            UUID(uuid_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def to_json_safe(obj: Any) -> str:
        """Best-effort JSON serialization with fallbacks."""
        try:
            return json.dumps(obj, default=str)
        except Exception:  # noqa: BLE001
            return '{"error":"json_serialization_failed"}'
