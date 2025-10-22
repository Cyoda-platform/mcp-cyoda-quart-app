"""
Unit tests for entity casting utilities.
"""

from typing import Optional

import pytest
from pydantic import Field

from common.entity.cyoda_entity import CyodaEntity
from common.entity.entity_casting import cast_entity, try_cast_entity


class SimpleEntity(CyodaEntity):
    """Simple test entity."""

    name: str
    value: int


class ExtendedEntity(CyodaEntity):
    """Extended test entity with additional fields."""

    name: str
    value: int
    description: Optional[str] = None


class DifferentEntity(CyodaEntity):
    """Different entity with different fields."""

    title: str
    count: int


class TestCastEntity:
    """Test suite for cast_entity function."""

    def test_cast_same_type(self):
        """Test casting entity to its own type."""
        entity = SimpleEntity(name="test", value=42)

        result = cast_entity(entity, SimpleEntity)

        assert result is entity
        assert isinstance(result, SimpleEntity)

    def test_cast_to_compatible_type(self):
        """Test casting to compatible type with same fields."""
        entity = SimpleEntity(name="test", value=42)

        result = cast_entity(entity, ExtendedEntity)

        assert isinstance(result, ExtendedEntity)
        assert result.name == "test"
        assert result.value == 42
        assert result.description is None

    def test_cast_from_extended_to_simple(self):
        """Test casting from extended type to simple type."""
        entity = ExtendedEntity(name="test", value=42, description="A test entity")

        result = cast_entity(entity, SimpleEntity)

        assert isinstance(result, SimpleEntity)
        assert result.name == "test"
        assert result.value == 42

    def test_cast_to_incompatible_type_fallback(self):
        """Test casting to incompatible type falls back to duck typing."""
        entity = SimpleEntity(name="test", value=42)

        # This should fail to create DifferentEntity but fallback to duck typing
        result = cast_entity(entity, DifferentEntity)

        # Result should be the original entity (duck typed)
        assert result is entity

    def test_cast_non_cyoda_entity_raises_error(self):
        """Test that casting to non-CyodaEntity type raises TypeError."""
        entity = SimpleEntity(name="test", value=42)

        class NotAnEntity:
            pass

        with pytest.raises(TypeError) as exc_info:
            cast_entity(entity, NotAnEntity)

        assert "must be a subclass of CyodaEntity" in str(exc_info.value)

    def test_cast_preserves_technical_id(self):
        """Test that casting preserves technical_id."""
        entity = SimpleEntity(name="test", value=42)
        entity.technical_id = "test-id-123"

        result = cast_entity(entity, ExtendedEntity)

        assert result.technical_id == "test-id-123"

    def test_cast_preserves_lifecycle_state(self):
        """Test that casting preserves lifecycle state."""
        entity = SimpleEntity(name="test", value=42)
        entity.lifecycle_state = "VALIDATED"

        result = cast_entity(entity, ExtendedEntity)

        assert result.lifecycle_state == "VALIDATED"

    def test_cast_with_model_dump(self):
        """Test casting uses model_dump if available."""
        entity = SimpleEntity(name="test", value=42)

        # Ensure model_dump is used
        assert hasattr(entity, "model_dump")

        result = cast_entity(entity, ExtendedEntity)

        assert isinstance(result, ExtendedEntity)
        assert result.name == "test"

    def test_cast_handles_extra_fields(self):
        """Test casting handles extra fields gracefully."""
        entity = ExtendedEntity(name="test", value=42, description="extra")

        result = cast_entity(entity, SimpleEntity)

        # Should successfully cast, dropping the extra field
        assert isinstance(result, SimpleEntity)
        assert result.name == "test"
        assert result.value == 42


class TestTryCastEntity:
    """Test suite for try_cast_entity function."""

    def test_try_cast_success(self):
        """Test successful casting returns entity."""
        entity = SimpleEntity(name="test", value=42)

        result = try_cast_entity(entity, ExtendedEntity)

        assert result is not None
        assert isinstance(result, ExtendedEntity)
        assert result.name == "test"

    def test_try_cast_same_type(self):
        """Test try_cast with same type."""
        entity = SimpleEntity(name="test", value=42)

        result = try_cast_entity(entity, SimpleEntity)

        assert result is entity

    def test_try_cast_incompatible_type(self):
        """Test try_cast with incompatible type."""
        entity = SimpleEntity(name="test", value=42)

        # Should fallback to duck typing, not return None
        result = try_cast_entity(entity, DifferentEntity)

        # Duck typing fallback means it returns the original entity
        assert result is entity

    def test_try_cast_non_cyoda_entity_returns_none(self):
        """Test that try_cast with non-CyodaEntity returns None."""
        entity = SimpleEntity(name="test", value=42)

        class NotAnEntity:
            pass

        result = try_cast_entity(entity, NotAnEntity)

        assert result is None

    def test_try_cast_preserves_data(self):
        """Test that try_cast preserves entity data."""
        entity = SimpleEntity(name="test", value=42)
        entity.technical_id = "test-id-123"

        result = try_cast_entity(entity, ExtendedEntity)

        assert result is not None
        assert result.technical_id == "test-id-123"
        assert result.name == "test"
        assert result.value == 42


class TestEntityCastingEdgeCases:
    """Test edge cases in entity casting."""

    def test_cast_with_none_values(self):
        """Test casting entity with None values."""
        entity = ExtendedEntity(name="test", value=42, description=None)

        result = cast_entity(entity, SimpleEntity)

        assert isinstance(result, SimpleEntity)
        assert result.name == "test"

    def test_cast_with_default_values(self):
        """Test casting respects default values."""
        entity = SimpleEntity(name="test", value=42)

        result = cast_entity(entity, ExtendedEntity)

        # description should have default value None
        assert result.description is None

    def test_cast_chain(self):
        """Test chaining multiple casts."""
        entity = SimpleEntity(name="test", value=42)

        # Cast to extended
        extended = cast_entity(entity, ExtendedEntity)
        assert isinstance(extended, ExtendedEntity)

        # Cast back to simple
        simple = cast_entity(extended, SimpleEntity)
        assert isinstance(simple, SimpleEntity)
        assert simple.name == "test"
        assert simple.value == 42

    def test_cast_with_validation_error(self):
        """Test casting when validation fails."""

        class StrictEntity(CyodaEntity):
            name: str
            value: int = Field(gt=0)  # Must be greater than 0

        entity = SimpleEntity(name="test", value=-1)

        # Should fallback to duck typing when validation fails
        result = cast_entity(entity, StrictEntity)

        # Fallback means original entity is returned
        assert result is entity

