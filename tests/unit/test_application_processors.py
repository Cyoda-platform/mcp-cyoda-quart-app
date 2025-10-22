"""
Unit tests for application processors.

This module provides template tests for application processors.
Extend these tests with your specific processor implementations.
"""

from unittest.mock import patch

import pytest

from application.entity.adoption_request import AdoptionRequest
from application.processor.adoption_request_processor import AdoptionRequestProcessor
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


class TestAdoptionRequestProcessorInitialization:
    """Test suite for AdoptionRequestProcessor initialization."""

    def test_processor_initialization(self) -> None:
        """Test AdoptionRequestProcessor initialization."""
        processor = AdoptionRequestProcessor()

        assert processor.name == "AdoptionRequestProcessor"
        assert processor.description == "Processes approved adoption requests"
        assert processor.logger is not None

    def test_processor_has_required_attributes(self) -> None:
        """Test that processor has required attributes."""
        processor = AdoptionRequestProcessor()

        assert hasattr(processor, "name")
        assert hasattr(processor, "description")
        assert hasattr(processor, "logger")
        assert hasattr(processor, "process")


class TestAdoptionRequestProcessorProcessing:
    """Test suite for AdoptionRequestProcessor processing."""

    @pytest.mark.asyncio
    async def test_process_adoption_request(self) -> None:
        """Test processing an adoption request."""
        processor = AdoptionRequestProcessor()
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        # Process should not raise an exception
        await processor.process(request)

    @pytest.mark.asyncio
    async def test_process_with_kwargs(self) -> None:
        """Test processing with additional kwargs."""
        processor = AdoptionRequestProcessor()
        request = AdoptionRequest(
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            applicant_phone="555-1234",
            reason_for_adoption="Family pet",
            family_size=2,
            living_situation="Apartment",
            experience_level="INTERMEDIATE",
        )

        # Process should handle kwargs without error
        await processor.process(request, extra_param="value")

    @pytest.mark.asyncio
    async def test_process_logs_processing_info(self) -> None:
        """Test that processor logs processing information."""
        processor = AdoptionRequestProcessor()
        request = AdoptionRequest(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="ADVANCED",
        )

        with patch.object(processor.logger, "info") as mock_info:
            await processor.process(request)
            # Should log at least the processing start and completion
            assert mock_info.call_count >= 2

    @pytest.mark.asyncio
    async def test_process_handles_exception(self) -> None:
        """Test that processor handles exceptions gracefully."""
        processor = AdoptionRequestProcessor()
        # Create an invalid entity that will cause an error during casting
        invalid_entity = CyodaEntity()

        with pytest.raises(Exception):
            await processor.process(invalid_entity)

    @pytest.mark.asyncio
    async def test_process_logs_error_on_exception(self) -> None:
        """Test that processor logs errors when exception occurs."""
        processor = AdoptionRequestProcessor()
        invalid_entity = CyodaEntity()

        with patch.object(processor.logger, "error") as mock_error:
            with pytest.raises(Exception):
                await processor.process(invalid_entity)
            # Should log the error
            assert mock_error.call_count >= 1
