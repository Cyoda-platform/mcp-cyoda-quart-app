"""
Entity Models with Validation.

This module provides validated entity models using Pydantic for robust
data validation and serialization.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional, Union

from common.models.base import (
    PYDANTIC_AVAILABLE,
    BaseValidatedModel,
    EntityType,
    ValidationUtils,
)

if PYDANTIC_AVAILABLE:
    # Pydantic v2 APIs
    from pydantic import ConfigDict, Field, field_validator, model_validator
else:
    # Lightweight stubs to keep runtime import errors away if Pydantic isn't present.
    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore  # noqa: N802
        return None

    def field_validator(*_fields: str, **_kwargs: Any):  # type: ignore[no-untyped-def,no-redef]
        def decorator(fn):  # type: ignore[no-untyped-def]
            return fn

        return decorator

    def model_validator(*_args: Any, **_kwargs: Any):  # type: ignore[no-untyped-def,no-redef]
        def decorator(fn):  # type: ignore[no-untyped-def]
            return fn

        return decorator

    class ConfigDict(dict):  # type: ignore
        pass


class ValidatedCyodaEntity(BaseValidatedModel):
    """Validated Cyoda entity model with comprehensive validation."""

    entity_id: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            pattern=r"^[a-zA-Z0-9_-]+$",
            description="Unique entity identifier",
        ),
    ]
    entity_type: EntityType = Field(..., description="Type of entity")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Entity creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Entity last update timestamp",
    )
    version: Annotated[int, Field(ge=1, description="Entity version number")] = 1

    # Core entity data
    name: Optional[Annotated[str, Field(max_length=255)]] = Field(
        None, description="Entity name"
    )
    description: Optional[Annotated[str, Field(max_length=1000)]] = Field(
        None, description="Entity description"
    )
    status: Optional[str] = Field(default="active", description="Entity status")

    # Metadata and custom fields
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Entity metadata"
    )
    tags: List[str] = Field(default_factory=list, description="Entity tags")

    # Relationships
    parent_id: Optional[str] = Field(None, description="Parent entity ID")
    children_ids: List[str] = Field(
        default_factory=list, description="Child entity IDs"
    )

    # Processing information
    processing_status: Optional[str] = Field(
        None, description="Current processing status"
    )
    last_processed_at: Optional[datetime] = Field(
        None, description="Last processing timestamp"
    )
    processing_errors: List[str] = Field(
        default_factory=list, description="Processing errors"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_id": "entity-123",
                "entity_type": "EDGE_MESSAGE",
                "name": "Sample Entity",
                "description": "A sample entity for demonstration",
                "status": "active",
                "metadata": {"source": "api", "priority": "high"},
                "tags": ["important", "demo"],
            }
        }
    )

    # -----------------------
    # Validators (Pydantic v2)
    # -----------------------

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity ID format."""
        if not ValidationUtils.validate_entity_id(v):
            raise ValueError("Invalid entity ID format")
        return v.strip()

    @field_validator("created_at", "updated_at", "last_processed_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Optional[Union[str, datetime]]) -> Optional[datetime]:
        """Parse datetime from various formats."""
        if v is None:
            return v
        if isinstance(v, str):
            # Handle ISO format with Z suffix
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return datetime.fromisoformat(v)
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Any) -> List[str]:
        """Validate and normalize tags."""
        if not isinstance(v, list):
            return []

        validated_tags: List[str] = []
        for tag in v:
            if isinstance(tag, str) and len(tag.strip()) > 0:
                # Normalize tag format
                normalized_tag = tag.strip().lower().replace(" ", "_")
                if (
                    len(normalized_tag) <= 50
                    and normalized_tag.replace("_", "").replace("-", "").isalnum()
                ):
                    validated_tags.append(normalized_tag)

        # Remove duplicates while preserving order
        deduped: List[str] = []
        seen = set()
        for t in validated_tags:
            if t not in seen:
                seen.add(t)
                deduped.append(t)
        return deduped

    @field_validator("children_ids")
    @classmethod
    def validate_children_ids(cls, v: Any) -> List[str]:
        """Validate child entity IDs."""
        if not isinstance(v, list):
            return []

        validated_ids: List[str] = []
        for child_id in v:
            if isinstance(child_id, str) and ValidationUtils.validate_entity_id(
                child_id
            ):
                validated_ids.append(child_id.strip())

        # Remove duplicates while preserving order
        deduped: List[str] = []
        seen = set()
        for cid in validated_ids:
            if cid not in seen:
                seen.add(cid)
                deduped.append(cid)
        return deduped

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate parent entity ID."""
        if v is None:
            return v
        if not ValidationUtils.validate_entity_id(v):
            raise ValueError("Invalid parent entity ID format")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> str:
        """Validate entity status."""
        if v is None:
            return "active"

        valid_statuses = ["active", "inactive", "pending", "archived", "deleted"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")

        return v.lower()

    @field_validator("processing_status")
    @classmethod
    def validate_processing_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate processing status."""
        if v is None:
            return v

        valid_statuses = ["pending", "processing", "completed", "failed", "cancelled"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Processing status must be one of: {valid_statuses}")

        return v.lower()

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Any) -> Dict[str, Any]:
        """Validate metadata structure."""
        if not isinstance(v, dict):
            return {}

        # Ensure metadata keys are strings and values are serializable
        validated_metadata: Dict[str, Any] = {}
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

    @model_validator(mode="after")
    def validate_entity_consistency(self) -> "ValidatedCyodaEntity":
        """Validate entity consistency after model creation."""
        # Ensure updated_at is not before created_at
        if self.created_at and self.updated_at and self.updated_at < self.created_at:
            self.updated_at = self.created_at

        # Ensure entity doesn't reference itself as parent
        if self.entity_id and self.parent_id and self.entity_id == self.parent_id:
            self.parent_id = None

        # Ensure entity doesn't reference itself in children
        if self.entity_id and self.children_ids and self.entity_id in self.children_ids:
            self.children_ids = [
                cid for cid in self.children_ids if cid != self.entity_id
            ]

        return self

    # -----------------------
    # Convenience methods
    # -----------------------

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the entity."""
        if isinstance(key, str) and len(key) <= 100:
            try:
                import json

                json.dumps(value)  # Ensure value is serializable
                self.metadata[key] = value
                self.updated_at = datetime.now(timezone.utc)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Metadata value for key '{key}' is not serializable"
                ) from exc

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
            normalized_tag = tag.strip().lower().replace(" ", "_")
            if (
                len(normalized_tag) <= 50
                and normalized_tag.replace("_", "").replace("-", "").isalnum()
            ):
                if normalized_tag not in self.tags:
                    self.tags.append(normalized_tag)
                    self.updated_at = datetime.now(timezone.utc)

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the entity."""
        normalized_tag = tag.strip().lower().replace(" ", "_")
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag."""
        normalized_tag = tag.strip().lower().replace(" ", "_")
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

    @classmethod
    def from_legacy_entity(cls, legacy_entity: Any) -> "ValidatedCyodaEntity":
        """Create from legacy CyodaEntity."""
        # Extract basic fields
        entity_data: Dict[str, Any] = {
            "entity_id": legacy_entity.entity_id,
            "entity_type": legacy_entity.entity_type,
            "created_at": legacy_entity.created_at,
        }

        # Extract metadata
        if hasattr(legacy_entity, "metadata") and legacy_entity.metadata:
            # Copy to avoid mutating legacy object
            entity_data["metadata"] = dict(legacy_entity.metadata)

            # Extract special fields from metadata
            for field in [
                "name",
                "description",
                "status",
                "tags",
                "parent_id",
                "children_ids",
                "processing_status",
                "processing_errors",
            ]:
                if field in entity_data["metadata"]:
                    entity_data[field] = entity_data["metadata"].pop(field)

        return cls(**entity_data)
