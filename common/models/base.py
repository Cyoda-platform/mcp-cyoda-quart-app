"""
Base Models and Validation.

This module provides base Pydantic models for data validation and serialization
with comprehensive validation rules and error handling.
"""

import re
from typing import Any, Dict, List, Optional, Union, Type, get_type_hints
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

try:
    from pydantic import BaseModel, Field, validator, root_validator, ConfigDict, ValidationError
    from pydantic.config import BaseConfig
    from pydantic.types import constr, conint, confloat
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    Field = lambda *args, **kwargs: None
    validator = lambda *args, **kwargs: lambda f: f
    root_validator = lambda *args, **kwargs: lambda f: f
    ValidationError = Exception
    constr = str
    conint = int
    confloat = float

from common.observability.logging import get_logger

logger = get_logger(__name__)


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


if PYDANTIC_AVAILABLE:
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
            json_encoders={
                datetime: lambda v: v.isoformat() if v else None,
                UUID: lambda v: str(v) if v else None,
            },
            # Schema extra information
            json_schema_extra={
                "example": {}
            }
        )
        
        def dict_safe(self, **kwargs) -> Dict[str, Any]:
            """Convert to dictionary with safe serialization."""
            try:
                return self.dict(**kwargs)
            except Exception as e:
                logger.warning(f"Failed to serialize model: {e}")
                return {"error": "serialization_failed", "type": self.__class__.__name__}
        
        def json_safe(self, **kwargs) -> str:
            """Convert to JSON with safe serialization."""
            try:
                return self.json(**kwargs)
            except Exception as e:
                logger.warning(f"Failed to serialize model to JSON: {e}")
                return '{"error": "json_serialization_failed"}'
        
        @classmethod
        def validate_data(cls, data: Dict[str, Any]) -> 'BaseValidatedModel':
            """Validate data and return model instance."""
            try:
                return cls(**data)
            except ValidationError as e:
                logger.error(f"Validation failed for {cls.__name__}: {e}")
                raise
        
        @classmethod
        def from_dict_safe(cls, data: Dict[str, Any]) -> Optional['BaseValidatedModel']:
            """Create instance from dictionary with error handling."""
            try:
                return cls(**data)
            except ValidationError as e:
                logger.warning(f"Failed to create {cls.__name__} from dict: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error creating {cls.__name__}: {e}")
                return None


    class EntityMetadata(BaseValidatedModel):
        """Entity metadata model."""
        
        created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        created_by: Optional[str] = Field(None, description="User who created the entity")
        updated_by: Optional[str] = Field(None, description="User who last updated the entity")
        version: int = Field(default=1, ge=1, description="Entity version number")
        tags: List[str] = Field(default_factory=list, description="Entity tags")
        custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")
        
        @validator('created_at', 'updated_at', pre=True)
        def parse_datetime(cls, v):
            """Parse datetime from various formats."""
            if isinstance(v, str):
                # Handle ISO format with Z suffix
                if v.endswith('Z'):
                    v = v[:-1] + '+00:00'
                return datetime.fromisoformat(v)
            return v
        
        @validator('tags')
        def validate_tags(cls, v):
            """Validate tags format."""
            if not isinstance(v, list):
                return []
            
            validated_tags = []
            for tag in v:
                if isinstance(tag, str) and re.match(r'^[a-zA-Z0-9_-]+$', tag):
                    validated_tags.append(tag.lower())
            
            return validated_tags


    class EntityId(BaseValidatedModel):
        """Entity identifier model."""
        
        entity_id: constr(min_length=1, max_length=100, regex=r'^[a-zA-Z0-9_-]+$') = Field(
            ..., description="Unique entity identifier"
        )
        entity_type: EntityType = Field(..., description="Type of entity")
        
        @validator('entity_id')
        def validate_entity_id(cls, v):
            """Validate entity ID format."""
            if not v or not isinstance(v, str):
                raise ValueError("Entity ID must be a non-empty string")
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Entity ID contains invalid characters")
            
            return v.strip()


    class ProcessorRequest(BaseValidatedModel):
        """Processor request model."""
        
        processor_name: constr(min_length=1, max_length=50, regex=r'^[a-zA-Z0-9_-]+$') = Field(
            ..., description="Name of the processor to execute"
        )
        entity_id: constr(min_length=1, max_length=100) = Field(
            ..., description="ID of the entity to process"
        )
        request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request ID")
        correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
        parameters: Dict[str, Any] = Field(default_factory=dict, description="Processor parameters")
        timeout_seconds: confloat(gt=0, le=300) = Field(default=30, description="Processing timeout")
        priority: conint(ge=1, le=10) = Field(default=5, description="Processing priority")
        
        @validator('processor_name')
        def validate_processor_name(cls, v):
            """Validate processor name format."""
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Processor name contains invalid characters")
            return v.lower()
        
        @validator('parameters')
        def validate_parameters(cls, v):
            """Validate processor parameters."""
            if not isinstance(v, dict):
                return {}
            
            # Ensure all keys are strings
            validated_params = {}
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
        result: Optional[Dict[str, Any]] = Field(None, description="Processing result")
        error_message: Optional[str] = Field(None, description="Error message if failed")
        error_code: Optional[str] = Field(None, description="Error code if failed")
        processing_time_ms: confloat(ge=0) = Field(..., description="Processing time in milliseconds")
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
        
        @validator('status')
        def validate_status_consistency(cls, v, values):
            """Validate status consistency with other fields."""
            if v == ProcessingStatus.FAILED:
                if not values.get('error_message'):
                    raise ValueError("Error message required for failed status")
            elif v == ProcessingStatus.COMPLETED:
                if values.get('error_message'):
                    raise ValueError("Error message not allowed for completed status")
            
            return v


    class CriteriaRequest(BaseValidatedModel):
        """Criteria check request model."""
        
        criteria_name: constr(min_length=1, max_length=50, regex=r'^[a-zA-Z0-9_-]+$') = Field(
            ..., description="Name of the criteria to check"
        )
        entity_id: constr(min_length=1, max_length=100) = Field(
            ..., description="ID of the entity to check"
        )
        request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request ID")
        correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
        parameters: Dict[str, Any] = Field(default_factory=dict, description="Criteria parameters")
        
        @validator('criteria_name')
        def validate_criteria_name(cls, v):
            """Validate criteria name format."""
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError("Criteria name contains invalid characters")
            return v.lower()


    class CriteriaResponse(BaseValidatedModel):
        """Criteria check response model."""
        
        request_id: str = Field(..., description="Original request ID")
        criteria_name: str = Field(..., description="Name of the criteria that was checked")
        entity_id: str = Field(..., description="ID of the checked entity")
        matches: bool = Field(..., description="Whether the entity matches the criteria")
        confidence: confloat(ge=0.0, le=1.0) = Field(default=1.0, description="Confidence score")
        details: Dict[str, Any] = Field(default_factory=dict, description="Detailed check results")
        processing_time_ms: confloat(ge=0) = Field(..., description="Check time in milliseconds")
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


    class HealthCheckResult(BaseValidatedModel):
        """Health check result model."""
        
        check_name: str = Field(..., description="Name of the health check")
        status: str = Field(..., description="Health check status")
        message: str = Field(default="", description="Health check message")
        duration_ms: confloat(ge=0) = Field(..., description="Check duration in milliseconds")
        timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        details: Dict[str, Any] = Field(default_factory=dict, description="Detailed check information")
        
        @validator('status')
        def validate_status(cls, v):
            """Validate health check status."""
            valid_statuses = ['healthy', 'degraded', 'unhealthy', 'unknown']
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
            return v.lower()


    class ConfigurationModel(BaseValidatedModel):
        """Configuration model with validation."""
        
        section: str = Field(..., description="Configuration section name")
        key: str = Field(..., description="Configuration key")
        value: Any = Field(..., description="Configuration value")
        data_type: str = Field(..., description="Value data type")
        description: Optional[str] = Field(None, description="Configuration description")
        required: bool = Field(default=False, description="Whether the configuration is required")
        sensitive: bool = Field(default=False, description="Whether the configuration contains sensitive data")
        
        @validator('section', 'key')
        def validate_identifiers(cls, v):
            """Validate configuration identifiers."""
            if not re.match(r'^[a-zA-Z0-9._-]+$', v):
                raise ValueError("Invalid identifier format")
            return v.lower()
        
        @validator('data_type')
        def validate_data_type(cls, v):
            """Validate data type."""
            valid_types = ['string', 'integer', 'float', 'boolean', 'list', 'dict']
            if v.lower() not in valid_types:
                raise ValueError(f"Data type must be one of: {valid_types}")
            return v.lower()

else:
    # Fallback implementations when Pydantic is not available
    class BaseValidatedModel:
        """Fallback base model without validation."""
        
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict_safe(self, **kwargs) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        def json_safe(self, **kwargs) -> str:
            """Convert to JSON string."""
            import json
            return json.dumps(self.dict_safe(), default=str)
        
        @classmethod
        def validate_data(cls, data: Dict[str, Any]):
            """Create instance without validation."""
            return cls(**data)
        
        @classmethod
        def from_dict_safe(cls, data: Dict[str, Any]):
            """Create instance from dictionary."""
            return cls(**data)
    
    # Create fallback classes
    EntityMetadata = BaseValidatedModel
    EntityId = BaseValidatedModel
    ProcessorRequest = BaseValidatedModel
    ProcessorResponse = BaseValidatedModel
    CriteriaRequest = BaseValidatedModel
    CriteriaResponse = BaseValidatedModel
    HealthCheckResult = BaseValidatedModel
    ConfigurationModel = BaseValidatedModel


def validate_model_data(model_class: Type[BaseValidatedModel], data: Dict[str, Any]) -> BaseValidatedModel:
    """Validate data against a model class."""
    if not PYDANTIC_AVAILABLE:
        logger.warning("Pydantic not available. Validation skipped.")
        return model_class(**data)
    
    try:
        return model_class.validate_data(data)
    except ValidationError as e:
        logger.error(f"Validation failed for {model_class.__name__}: {e}")
        raise


def is_pydantic_available() -> bool:
    """Check if Pydantic is available."""
    return PYDANTIC_AVAILABLE


# Validation utilities
class ValidationUtils:
    """Utility functions for data validation."""

    @staticmethod
    def validate_entity_id(entity_id: str) -> bool:
        """Validate entity ID format."""
        if not entity_id or not isinstance(entity_id, str):
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', entity_id.strip()))

    @staticmethod
    def validate_processor_name(processor_name: str) -> bool:
        """Validate processor name format."""
        if not processor_name or not isinstance(processor_name, str):
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', processor_name.strip()))

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            return str(value)[:max_length]
        return value.strip()[:max_length]

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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
