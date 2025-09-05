"""
Base CyodaEntity class that all entities should inherit from.
Provides common fields and methods for entity management.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CyodaEntity(BaseModel):
    """
    Base class for all Cyoda entities.
    Provides common fields and functionality that all entities should have.
    """
    
    # Common entity fields
    entity_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique entity identifier")
    technical_id: Optional[str] = Field(default=None, description="Technical ID assigned by Cyoda platform")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'), description="Entity creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Entity last update timestamp")
    version: Optional[str] = Field(default="1.0", description="Entity version")
    
    # Workflow-related fields
    state: Optional[str] = Field(default="none", description="Current workflow state")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        # Allow extra fields for flexibility
        extra="allow",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignment
        validate_assignment=True,
        # Allow population by field name or alias
        populate_by_name=True
    )
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def set_state(self, new_state: str) -> None:
        """Update entity state and timestamp"""
        self.state = new_state
        self.update_timestamp()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update metadata field"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        self.update_timestamp()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata field value"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert entity to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CyodaEntity':
        """Create entity instance from dictionary"""
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of the entity"""
        return f"{self.__class__.__name__}(entity_id={self.entity_id}, state={self.state})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the entity"""
        return f"{self.__class__.__name__}({self.dict()})"
