"""
Unit tests for application criteria.

This module provides template tests for application criteria checkers.
Extend these tests with your specific criteria implementations.
"""

import pytest

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker


class TemplateApplicationEntity(CyodaEntity):
    """Template entity for criteria testing."""

    name: str
    value: int


class TemplateApplicationCriteria(CyodaCriteriaChecker):
    """Template criteria checker for application testing."""

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if entity meets criteria."""
        if isinstance(entity, TemplateApplicationEntity):
            return entity.value > 0
        return False


class TestApplicationCriteriaBasics:
    """Test suite for basic application criteria functionality."""

    def test_criteria_initialization(self) -> None:
        """Test criteria initialization."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        assert criteria.name == "TestCriteria"
        assert criteria.description == "A test criteria"
        assert criteria.logger is not None

    def test_criteria_has_required_attributes(self) -> None:
        """Test that criteria has required attributes."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        assert hasattr(criteria, "name")
        assert hasattr(criteria, "description")
        assert hasattr(criteria, "logger")
        assert hasattr(criteria, "check")

    @pytest.mark.asyncio
    async def test_criteria_check_method_true(self) -> None:
        """Test criteria check method returns True."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        entity = TemplateApplicationEntity(name="Test", value=5)
        result = await criteria.check(entity)

        assert result is True

    @pytest.mark.asyncio
    async def test_criteria_check_method_false(self) -> None:
        """Test criteria check method returns False."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        entity = TemplateApplicationEntity(name="Test", value=-5)
        result = await criteria.check(entity)

        assert result is False

    @pytest.mark.asyncio
    async def test_criteria_with_kwargs(self) -> None:
        """Test criteria with additional kwargs."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        entity = TemplateApplicationEntity(name="Test", value=10)
        result = await criteria.check(entity, extra_param="value")

        assert result is True

    def test_criteria_string_representation(self) -> None:
        """Test criteria string representation."""
        criteria = TemplateApplicationCriteria(
            name="TestCriteria", description="A test criteria"
        )

        criteria_str = str(criteria)
        assert "TestCriteria" in criteria_str or "test" in criteria_str.lower()
