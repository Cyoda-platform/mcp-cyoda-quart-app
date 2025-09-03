"""
Entity Models with Validation.

This module provides validated entity models using Pydantic for robust
data validation and serialization.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from uuid import uuid4

from common.models.base import (
    BaseValidatedModel, EntityType, EntityMetadata, ValidationUtils,
    PYDANTIC_AVAILABLE
)

if PYDANTIC_AVAILABLE:
    from pydantic import Field, validator, root_validator, ConfigDict
    from pydantic.types import constr, conint
else:
    Field = lambda *args, **kwargs: None
    validator = lambda *args, **kwargs: lambda f: f
    root_validator = lambda *args, **kwargs: lambda f: f
    constr = str
    conint = int


class ValidatedCyodaEntity(BaseValidatedModel):
    """Validated Cyoda entity model with comprehensive validation."""
    
    entity_id: constr(min_length=1, max_length=100, regex=r'^[a-zA-Z0-9_-]+$') = Field(
        ..., description="Unique entity identifier"
    )
    entity_type: EntityType = Field(..., description="Type of entity")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Entity creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Entity last update timestamp"
    )
    version: conint(ge=1) = Field(default=1, description="Entity version number")
    
    # Core entity data
    name: Optional[constr(max_length=255)] = Field(None, description="Entity name")
    description: Optional[constr(max_length=1000)] = Field(None, description="Entity description")
    status: Optional[str] = Field(default="active", description="Entity status")
    
    # Metadata and custom fields
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Entity metadata")
    tags: List[str] = Field(default_factory=list, description="Entity tags")
    
    # Relationships
    parent_id: Optional[str] = Field(None, description="Parent entity ID")
    children_ids: List[str] = Field(default_factory=list, description="Child entity IDs")
    
    # Processing information
    processing_status: Optional[str] = Field(None, description="Current processing status")
    last_processed_at: Optional[datetime] = Field(None, description="Last processing timestamp")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_id": "entity-123",
                "entity_type": "EDGE_MESSAGE",
                "name": "Sample Entity",
                "description": "A sample entity for demonstration",
                "status": "active",
                "metadata": {
                    "source": "api",
                    "priority": "high"
                },
                "tags": ["important", "demo"]
            }
        }
    )
    
    @validator('entity_id')
    def validate_entity_id(cls, v):
        """Validate entity ID format."""
        if not ValidationUtils.validate_entity_id(v):
            raise ValueError("Invalid entity ID format")
        return v.strip()
    
    @validator('created_at', 'updated_at', 'last_processed_at', pre=True)
    def parse_datetime(cls, v):
        """Parse datetime from various formats."""
        if v is None:
            return v
        if isinstance(v, str):
            # Handle ISO format with Z suffix
            if v.endswith('Z'):
                v = v[:-1] + '+00:00'
            return datetime.fromisoformat(v)
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate and normalize tags."""
        if not isinstance(v, list):
            return []
        
        validated_tags = []
        for tag in v:
            if isinstance(tag, str) and len(tag.strip()) > 0:
                # Normalize tag format
                normalized_tag = tag.strip().lower().replace(' ', '_')
                if len(normalized_tag) <= 50 and normalized_tag.replace('_', '').replace('-', '').isalnum():
                    validated_tags.append(normalized_tag)
        
        return list(set(validated_tags))  # Remove duplicates
    
    @validator('children_ids')
    def validate_children_ids(cls, v):
        """Validate child entity IDs."""
        if not isinstance(v, list):
            return []
        
        validated_ids = []
        for child_id in v:
            if isinstance(child_id, str) and ValidationUtils.validate_entity_id(child_id):
                validated_ids.append(child_id.strip())
        
        return list(set(validated_ids))  # Remove duplicates
    
    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent entity ID."""
        if v is None:
            return v
        if not ValidationUtils.validate_entity_id(v):
            raise ValueError("Invalid parent entity ID format")
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        """Validate entity status."""
        if v is None:
            return "active"
        
        valid_statuses = ['active', 'inactive', 'pending', 'archived', 'deleted']
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        return v.lower()
    
    @validator('processing_status')
    def validate_processing_status(cls, v):
        """Validate processing status."""
        if v is None:
            return v
        
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v.lower() not in valid_statuses:
            raise ValueError(f"Processing status must be one of: {valid_statuses}")
        
        return v.lower()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata structure."""
        if not isinstance(v, dict):
            return {}
        
        # Ensure metadata keys are strings and values are serializable
        validated_metadata = {}
        for key, value in v.items():
            if isinstance(key, str) and len(key) <= 100:
                # Ensure value is JSON serializable
                try:
                    import json
                    json.dumps(value)
                    validated_metadata[key] = value
                except (TypeError, ValueError):
                    # Skip non-serializable values
                    continue
        
        return validated_metadata
    
    @root_validator
    def validate_entity_consistency(cls, values):
        """Validate entity consistency."""
        # Ensure updated_at is not before created_at
        created_at = values.get('created_at')
        updated_at = values.get('updated_at')
        
        if created_at and updated_at and updated_at < created_at:
            values['updated_at'] = created_at
        
        # Ensure entity doesn't reference itself as parent
        entity_id = values.get('entity_id')
        parent_id = values.get('parent_id')
        
        if entity_id and parent_id and entity_id == parent_id:
            values['parent_id'] = None
        
        # Ensure entity doesn't reference itself in children
        children_ids = values.get('children_ids', [])
        if entity_id and entity_id in children_ids:
            children_ids.remove(entity_id)
            values['children_ids'] = children_ids
        
        return values
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the entity."""
        if isinstance(key, str) and len(key) <= 100:
            try:
                import json
                json.dumps(value)  # Ensure value is serializable
                self.metadata[key] = value
                self.updated_at = datetime.now(timezone.utc)
            except (TypeError, ValueError):
                raise ValueError(f"Metadata value for key '{key}' is not serializable")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def remove_metadata(self, key: str) -> bool:
        """Remove metadata key."""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the entity."""
        if isinstance(tag, str) and len(tag.strip()) > 0:
            normalized_tag = tag.strip().lower().replace(' ', '_')
            if len(normalized_tag) <= 50 and normalized_tag.replace('_', '').replace('-', '').isalnum():
                if normalized_tag not in self.tags:
                    self.tags.append(normalized_tag)
                    self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the entity."""
        normalized_tag = tag.strip().lower().replace(' ', '_')
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag."""
        normalized_tag = tag.strip().lower().replace(' ', '_')
        return normalized_tag in self.tags
    
    def add_processing_error(self, error: str) -> None:
        """Add a processing error."""
        if isinstance(error, str) and len(error.strip()) > 0:
            error_msg = error.strip()[:500]  # Limit error message length
            if error_msg not in self.processing_errors:
                self.processing_errors.append(error_msg)
                self.updated_at = datetime.now(timezone.utc)
    
    def clear_processing_errors(self) -> None:
        """Clear all processing errors."""
        if self.processing_errors:
            self.processing_errors.clear()
            self.updated_at = datetime.now(timezone.utc)
    
    def mark_processed(self, status: str = "completed") -> None:
        """Mark entity as processed."""
        self.processing_status = status
        self.last_processed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

        return legacy_entity
    
    @classmethod
    def from_legacy_entity(cls, legacy_entity) -> 'ValidatedCyodaEntity':
        """Create from legacy CyodaEntity."""
        # Extract basic fields
        entity_data = {
            "entity_id": legacy_entity.entity_id,
            "entity_type": legacy_entity.entity_type,
            "created_at": legacy_entity.created_at
        }
        
        # Extract metadata
        if hasattr(legacy_entity, 'metadata') and legacy_entity.metadata:
            entity_data["metadata"] = legacy_entity.metadata.copy()
            
            # Extract special fields from metadata
            for field in ['name', 'description', 'status', 'tags', 'parent_id', 
                         'children_ids', 'processing_status', 'processing_errors']:
                if field in entity_data["metadata"]:
                    entity_data[field] = entity_data["metadata"].pop(field)
        
        return cls(**entity_data)
