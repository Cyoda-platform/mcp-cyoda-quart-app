"""
Unit tests for processor base classes.
"""

import pytest

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker, CyodaProcessor


class SampleEntity(CyodaEntity):
    """Sample entity for processor tests."""

    name: str
    value: int


class SampleProcessor(CyodaProcessor):
    """Sample processor implementation."""

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Sample process implementation."""
        if isinstance(entity, SampleEntity):
            entity.value += 1
        return entity


class SampleCriteriaChecker(CyodaCriteriaChecker):
    """Sample criteria checker implementation."""

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Sample check implementation."""
        if isinstance(entity, SampleEntity):
            return entity.value > 0
        return False


class TestCyodaProcessor:
    """Test suite for CyodaProcessor base class."""

    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = SampleProcessor(name="TestProc", description="A test processor")

        assert processor.name == "TestProc"
        assert processor.description == "A test processor"
        assert processor.logger is not None

    def test_processor_initialization_without_description(self):
        """Test processor initialization without description."""
        processor = SampleProcessor(name="TestProc")

        assert processor.name == "TestProc"
        assert processor.description == ""

    @pytest.mark.asyncio
    async def test_processor_process(self):
        """Test processor process method."""
        processor = SampleProcessor(name="TestProc")
        entity = SampleEntity(name="test", value=10)

        result = await processor.process(entity)

        assert isinstance(result, SampleEntity)
        assert result.value == 11

    @pytest.mark.asyncio
    async def test_processor_process_with_kwargs(self):
        """Test processor process with additional kwargs."""
        processor = SampleProcessor(name="TestProc")
        entity = SampleEntity(name="test", value=10)

        result = await processor.process(entity, extra_param="value")

        assert isinstance(result, SampleEntity)

    def test_processor_get_info(self):
        """Test processor get_info method."""
        processor = SampleProcessor(name="TestProc", description="A test processor")

        info = processor.get_info()

        assert info["name"] == "TestProc"
        assert info["description"] == "A test processor"
        assert info["class"] == "SampleProcessor"
        assert "module" in info

    def test_processor_str_representation(self):
        """Test processor string representation."""
        processor = SampleProcessor(name="TestProc", description="A test processor")

        str_repr = str(processor)

        assert "TestProc" in str_repr

    def test_processor_repr_representation(self):
        """Test processor repr representation."""
        processor = SampleProcessor(name="TestProc", description="A test processor")

        repr_str = repr(processor)

        assert "SampleProcessor" in repr_str
        assert "TestProc" in repr_str


class TestCyodaCriteriaChecker:
    """Test suite for CyodaCriteriaChecker base class."""

    def test_criteria_initialization(self):
        """Test criteria checker initialization."""
        criteria = SampleCriteriaChecker(name="TestCriteria", description="A test criteria")

        assert criteria.name == "TestCriteria"
        assert criteria.description == "A test criteria"
        assert criteria.logger is not None

    def test_criteria_initialization_without_description(self):
        """Test criteria initialization without description."""
        criteria = SampleCriteriaChecker(name="TestCriteria")

        assert criteria.name == "TestCriteria"
        assert criteria.description == ""

    @pytest.mark.asyncio
    async def test_criteria_check_true(self):
        """Test criteria check returns True."""
        criteria = SampleCriteriaChecker(name="TestCriteria")
        entity = SampleEntity(name="test", value=10)

        result = await criteria.check(entity)

        assert result is True

    @pytest.mark.asyncio
    async def test_criteria_check_false(self):
        """Test criteria check returns False."""
        criteria = SampleCriteriaChecker(name="TestCriteria")
        entity = SampleEntity(name="test", value=-5)

        result = await criteria.check(entity)

        assert result is False

    @pytest.mark.asyncio
    async def test_criteria_check_with_kwargs(self):
        """Test criteria check with additional kwargs."""
        criteria = SampleCriteriaChecker(name="TestCriteria")
        entity = SampleEntity(name="test", value=10)

        result = await criteria.check(entity, extra_param="value")

        assert result is True

    def test_criteria_get_info(self):
        """Test criteria get_info method."""
        criteria = SampleCriteriaChecker(name="TestCriteria", description="A test criteria")

        info = criteria.get_info()

        assert info["name"] == "TestCriteria"
        assert info["description"] == "A test criteria"
        assert info["class"] == "SampleCriteriaChecker"
        assert "module" in info

    def test_criteria_str_representation(self):
        """Test criteria string representation."""
        criteria = SampleCriteriaChecker(name="TestCriteria", description="A test criteria")

        str_repr = str(criteria)

        assert "TestCriteria" in str_repr

    def test_criteria_repr_representation(self):
        """Test criteria repr representation."""
        criteria = SampleCriteriaChecker(name="TestCriteria", description="A test criteria")

        repr_str = repr(criteria)

        assert "SampleCriteriaChecker" in repr_str
        assert "TestCriteria" in repr_str


class TestProcessorAbstractMethods:
    """Test that abstract methods must be implemented."""

    def test_processor_must_implement_process(self):
        """Test that processor must implement process method."""

        class IncompleteProcessor(CyodaProcessor):
            pass

        with pytest.raises(TypeError):
            IncompleteProcessor(name="Incomplete")

    def test_criteria_must_implement_check(self):
        """Test that criteria must implement check method."""

        class IncompleteCriteria(CyodaCriteriaChecker):
            pass

        with pytest.raises(TypeError):
            IncompleteCriteria(name="Incomplete")


class TestProcessorLogging:
    """Test processor logging functionality."""

    def test_processor_logger_name(self):
        """Test that processor logger has correct name."""
        processor = SampleProcessor(name="TestProc")

        logger_name = processor.logger.name

        assert "SampleProcessor" in logger_name

    def test_criteria_logger_name(self):
        """Test that criteria logger has correct name."""
        criteria = SampleCriteriaChecker(name="TestCriteria")

        logger_name = criteria.logger.name

        assert "SampleCriteriaChecker" in logger_name

