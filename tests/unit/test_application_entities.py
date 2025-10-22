"""
Unit tests for application entities.

This module provides template tests for application entities.
Extend these tests with your specific entity implementations.
"""

import pytest
from pydantic import ValidationError

from common.entity.cyoda_entity import CyodaEntity


class TemplateApplicationEntity(CyodaEntity):
    """Template entity for application testing."""

    name: str
    description: str


class TestApplicationEntityBasics:
    """Test suite for basic application entity functionality."""

    def test_entity_creation(self) -> None:
        """Test creating an application entity."""
        entity = TemplateApplicationEntity(
            name="Test Entity",
            description="A test entity"
        )

        assert entity.name == "Test Entity"
        assert entity.description == "A test entity"
        assert entity.state == "none"

    def test_entity_with_state(self) -> None:
        """Test entity with initial state."""
        entity = TemplateApplicationEntity(
            name="Test Entity",
            description="A test entity",
            state="created"
        )

        assert entity.state == "created"

    def test_entity_validation_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            TemplateApplicationEntity(name="Test")  # type: ignore

    def test_entity_to_dict(self) -> None:
        """Test converting entity to dictionary."""
        entity = TemplateApplicationEntity(
            name="Test Entity",
            description="A test entity"
        )

        entity_dict = entity.model_dump()
        assert entity_dict["name"] == "Test Entity"
        assert entity_dict["description"] == "A test entity"

    def test_entity_state_transitions(self) -> None:
        """Test entity state management."""
        entity = TemplateApplicationEntity(
            name="Test Entity",
            description="A test entity"
        )

        # Initial state should be 'none'
        assert entity.state == "none"

        # Update state
        entity.state = "created"
        assert entity.state == "created"

    def test_entity_metadata(self) -> None:
        """Test entity metadata."""
        entity = TemplateApplicationEntity(
            name="Test Entity",
            description="A test entity"
        )

        # Check that entity has required metadata
        assert hasattr(entity, "state")
        assert hasattr(entity, "entity_id")
        assert entity.state is not None

