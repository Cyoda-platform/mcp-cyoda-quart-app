"""
Unit tests for application processors.

This module provides template tests for application processors.
Extend these tests with your specific processor implementations.
"""

import pytest

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaProcessor


class TemplateApplicationEntity(CyodaEntity):
    """Template entity for processor testing."""

    name: str
    value: int


class TemplateApplicationProcessor(CyodaProcessor):
    """Template processor for application testing."""

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process the entity."""
        if isinstance(entity, TemplateApplicationEntity):
            entity.value += 1
        return entity


class TestApplicationProcessorBasics:
    """Test suite for basic application processor functionality."""

    def test_processor_initialization(self) -> None:
        """Test processor initialization."""
        processor = TemplateApplicationProcessor(
            name="TestProcessor", description="A test processor"
        )

        assert processor.name == "TestProcessor"
        assert processor.description == "A test processor"
        assert processor.logger is not None

    def test_processor_has_required_attributes(self) -> None:
        """Test that processor has required attributes."""
        processor = TemplateApplicationProcessor(
            name="TestProcessor", description="A test processor"
        )

        assert hasattr(processor, "name")
        assert hasattr(processor, "description")
        assert hasattr(processor, "logger")
        assert hasattr(processor, "process")

    @pytest.mark.asyncio
    async def test_processor_process_method(self) -> None:
        """Test processor process method."""
        processor = TemplateApplicationProcessor(
            name="TestProcessor", description="A test processor"
        )

        entity = TemplateApplicationEntity(name="Test", value=5)
        result = await processor.process(entity)

        assert result.value == 6

    @pytest.mark.asyncio
    async def test_processor_with_kwargs(self) -> None:
        """Test processor with additional kwargs."""
        processor = TemplateApplicationProcessor(
            name="TestProcessor", description="A test processor"
        )

        entity = TemplateApplicationEntity(name="Test", value=10)
        result = await processor.process(entity, extra_param="value")

        assert result.value == 11

    def test_processor_string_representation(self) -> None:
        """Test processor string representation."""
        processor = TemplateApplicationProcessor(
            name="TestProcessor", description="A test processor"
        )

        processor_str = str(processor)
        assert "TestProcessor" in processor_str or "test" in processor_str.lower()
