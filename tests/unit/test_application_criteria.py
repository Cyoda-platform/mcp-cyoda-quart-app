"""
Unit tests for application criteria.

This module provides template tests for application criteria checkers.
Extend these tests with your specific criteria implementations.
"""

import pytest
from unittest.mock import patch

from common.entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from application.entity.adoption_request import AdoptionRequest
from application.criterion.adoption_request_criterion import (
    AdoptionRequestValidationCriterion,
)


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


class TestAdoptionRequestValidationCriterionInitialization:
    """Test suite for AdoptionRequestValidationCriterion initialization."""

    def test_criterion_initialization(self) -> None:
        """Test AdoptionRequestValidationCriterion initialization."""
        criterion = AdoptionRequestValidationCriterion()

        assert criterion.name == "AdoptionRequestValidationCriterion"
        assert "Validates" in criterion.description
        assert criterion.logger is not None

    def test_criterion_has_required_attributes(self) -> None:
        """Test that criterion has required attributes."""
        criterion = AdoptionRequestValidationCriterion()

        assert hasattr(criterion, "name")
        assert hasattr(criterion, "description")
        assert hasattr(criterion, "logger")
        assert hasattr(criterion, "check")


class TestAdoptionRequestValidationCriterionValidation:
    """Test suite for AdoptionRequestValidationCriterion validation logic."""

    @pytest.mark.asyncio
    async def test_valid_adoption_request_passes(self) -> None:
        """Test that a valid adoption request passes validation."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Love animals",
            family_size=3,
            living_situation="House with yard",
            experience_level="INTERMEDIATE",
        )

        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_adoption_request_with_all_fields_passes(self) -> None:
        """Test that a valid adoption request with all fields passes."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            applicant_phone="555-1234",
            reason_for_adoption="Family pet",
            family_size=2,
            living_situation="Apartment",
            experience_level="BEGINNER",
            has_other_pets=True,
        )

        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_adoption_request_advanced_level_passes(self) -> None:
        """Test that a valid adoption request with advanced level passes."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="Bob Johnson",
            applicant_email="bob@example.com",
            applicant_phone="555-5678",
            reason_for_adoption="Experienced pet owner",
            family_size=4,
            living_situation="Farm",
            experience_level="ADVANCED",
        )

        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_adoption_request_large_family_passes(self) -> None:
        """Test that a valid adoption request with large family passes."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="Alice Brown",
            applicant_email="alice@example.com",
            applicant_phone="555-9999",
            reason_for_adoption="Want to teach kids responsibility",
            family_size=5,
            living_situation="Large house with backyard",
            experience_level="INTERMEDIATE",
        )

        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_valid_adoption_request_single_person_passes(self) -> None:
        """Test that a valid adoption request from single person passes."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="Charlie Davis",
            applicant_email="charlie@example.com",
            applicant_phone="555-1111",
            reason_for_adoption="Companion",
            family_size=1,
            living_situation="Apartment",
            experience_level="BEGINNER",
        )

        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_all_valid_experience_levels_pass(self) -> None:
        """Test that all valid experience levels pass validation."""
        criterion = AdoptionRequestValidationCriterion()
        for level in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
            request = AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Love animals",
                family_size=3,
                living_situation="House with yard",
                experience_level=level,
            )

            result = await criterion.check(request)
            assert result is True

    @pytest.mark.asyncio
    async def test_criterion_logs_validation_info(self) -> None:
        """Test that criterion logs validation information."""
        criterion = AdoptionRequestValidationCriterion()
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Love animals",
            family_size=3,
            living_situation="House with yard",
            experience_level="INTERMEDIATE",
        )

        with patch.object(criterion.logger, "info") as mock_info:
            await criterion.check(request)
            # Should log validation start and success
            assert mock_info.call_count >= 1

    @pytest.mark.asyncio
    async def test_criterion_handles_exception(self) -> None:
        """Test that criterion handles exceptions gracefully."""
        criterion = AdoptionRequestValidationCriterion()
        invalid_entity = CyodaEntity()

        result = await criterion.check(invalid_entity)
        assert result is False

    @pytest.mark.asyncio
    async def test_criterion_logs_error_on_exception(self) -> None:
        """Test that criterion logs errors when exception occurs."""
        criterion = AdoptionRequestValidationCriterion()
        invalid_entity = CyodaEntity()

        with patch.object(criterion.logger, "error") as mock_error:
            await criterion.check(invalid_entity)
            # Should log the error
            assert mock_error.call_count >= 1
