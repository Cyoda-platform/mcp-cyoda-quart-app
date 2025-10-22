"""
Unit tests for application entities.

This module provides template tests for application entities.
Extend these tests with your specific entity implementations.
"""

import pytest
from pydantic import ValidationError

from application.entity.adoption_request import AdoptionRequest
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
            name="Test Entity", description="A test entity"
        )

        assert entity.name == "Test Entity"
        assert entity.description == "A test entity"
        assert entity.state == "initial_state"

    def test_entity_with_state(self) -> None:
        """Test entity with initial state."""
        entity = TemplateApplicationEntity(
            name="Test Entity", description="A test entity", state="created"
        )

        assert entity.state == "created"

    def test_entity_validation_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            TemplateApplicationEntity(name="Test")  # type: ignore

    def test_entity_to_dict(self) -> None:
        """Test converting entity to dictionary."""
        entity = TemplateApplicationEntity(
            name="Test Entity", description="A test entity"
        )

        entity_dict = entity.model_dump()
        assert entity_dict["name"] == "Test Entity"
        assert entity_dict["description"] == "A test entity"

    def test_entity_state_transitions(self) -> None:
        """Test entity state management."""
        entity = TemplateApplicationEntity(
            name="Test Entity", description="A test entity"
        )

        # Initial state should be 'initial_state'
        assert entity.state == "initial_state"

        # Update state
        entity.state = "created"
        assert entity.state == "created"

    def test_entity_metadata(self) -> None:
        """Test entity metadata."""
        entity = TemplateApplicationEntity(
            name="Test Entity", description="A test entity"
        )

        # Check that entity has required metadata
        assert hasattr(entity, "state")
        assert hasattr(entity, "entity_id")
        assert entity.state is not None


class TestAdoptionRequestEntityCreation:
    """Test suite for AdoptionRequest entity creation."""

    def test_adoption_request_creation_with_required_fields(self) -> None:
        """Test creating an AdoptionRequest with all required fields."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-1234",
            reason_for_adoption="Love animals",
            family_size=3,
            living_situation="House with yard",
            experience_level="INTERMEDIATE",
        )

        assert request.applicant_name == "John Doe"
        assert request.applicant_email == "john@example.com"
        assert request.applicant_phone == "555-1234"
        assert request.reason_for_adoption == "Love animals"
        assert request.family_size == 3
        assert request.living_situation == "House with yard"
        assert request.experience_level == "INTERMEDIATE"

    def test_adoption_request_with_optional_fields(self) -> None:
        """Test creating an AdoptionRequest with optional fields."""
        request = AdoptionRequest(
            applicant_name="Jane Smith",
            applicant_email="jane@example.com",
            applicant_phone="555-5678",
            reason_for_adoption="Family pet",
            family_size=2,
            living_situation="Apartment",
            experience_level="BEGINNER",
            has_other_pets=True,
            review_notes="Good candidate",
            approval_status="pending",
        )

        assert request.has_other_pets is True
        assert request.review_notes == "Good candidate"
        assert request.approval_status == "pending"

    def test_adoption_request_default_timestamps(self) -> None:
        """Test that AdoptionRequest has default timestamps."""
        request = AdoptionRequest(
            applicant_name="Test User",
            applicant_email="test@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test reason",
            family_size=1,
            living_situation="Test location",
            experience_level="ADVANCED",
        )

        assert request.created_at is not None
        assert request.updated_at is None


class TestAdoptionRequestValidation:
    """Test suite for AdoptionRequest field validation."""

    def test_applicant_name_validation_empty(self) -> None:
        """Test that empty applicant name is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="",
                applicant_email="test@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_applicant_name_validation_too_short(self) -> None:
        """Test that applicant name shorter than 2 chars is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="A",
                applicant_email="test@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_applicant_name_validation_too_long(self) -> None:
        """Test that applicant name longer than 100 chars is rejected."""
        long_name = "A" * 101
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name=long_name,
                applicant_email="test@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_applicant_email_validation_empty(self) -> None:
        """Test that empty email is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_applicant_email_validation_invalid_format(self) -> None:
        """Test that email without @ is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="invalidemail",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_applicant_phone_validation_empty(self) -> None:
        """Test that empty phone is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_reason_for_adoption_validation_empty(self) -> None:
        """Test that empty reason is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_reason_for_adoption_validation_too_long(self) -> None:
        """Test that reason longer than 500 chars is rejected."""
        long_reason = "A" * 501
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption=long_reason,
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_family_size_validation_zero(self) -> None:
        """Test that family size of 0 is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=0,
                living_situation="Test",
                experience_level="BEGINNER",
            )

    def test_living_situation_validation_empty(self) -> None:
        """Test that empty living situation is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="",
                experience_level="BEGINNER",
            )

    def test_living_situation_validation_too_long(self) -> None:
        """Test that living situation longer than 500 chars is rejected."""
        long_situation = "A" * 501
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation=long_situation,
                experience_level="BEGINNER",
            )

    def test_experience_level_validation_invalid(self) -> None:
        """Test that invalid experience level is rejected."""
        with pytest.raises(ValidationError):
            AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="INVALID",
            )

    def test_experience_level_validation_valid_levels(self) -> None:
        """Test that all valid experience levels are accepted."""
        for level in ["BEGINNER", "INTERMEDIATE", "ADVANCED"]:
            request = AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level=level,
            )
            assert request.experience_level == level


class TestAdoptionRequestBusinessLogic:
    """Test suite for AdoptionRequest business logic methods."""

    def test_update_timestamp(self) -> None:
        """Test that update_timestamp updates the updated_at field."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        original_updated_at = request.updated_at
        request.update_timestamp()
        assert request.updated_at is not None
        assert request.updated_at != original_updated_at

    def test_set_review_notes(self) -> None:
        """Test that set_review_notes updates notes and timestamp."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        request.set_review_notes("Good candidate")
        assert request.review_notes == "Good candidate"
        assert request.updated_at is not None

    def test_set_approval_status(self) -> None:
        """Test that set_approval_status updates status and reviewer."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        request.set_approval_status("approved", "reviewer-123")
        assert request.approval_status == "approved"
        assert request.reviewer_id == "reviewer-123"
        assert request.updated_at is not None

    def test_is_ready_for_review_true(self) -> None:
        """Test is_ready_for_review returns True when state is submitted."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            state="submitted",
        )

        assert request.is_ready_for_review() is True

    def test_is_ready_for_review_false(self) -> None:
        """Test is_ready_for_review returns False when state is not submitted."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            state="initial_state",
        )

        assert request.is_ready_for_review() is False

    def test_is_approved_true(self) -> None:
        """Test is_approved returns True when approval_status is approved."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            approval_status="approved",
        )

        assert request.is_approved() is True

    def test_is_approved_false(self) -> None:
        """Test is_approved returns False when approval_status is not approved."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            approval_status="pending",
        )

        assert request.is_approved() is False

    def test_is_approved_none(self) -> None:
        """Test is_approved returns False when approval_status is None."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        assert request.is_approved() is False

    def test_to_api_response(self) -> None:
        """Test to_api_response returns proper format."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            state="submitted",
        )

        response = request.to_api_response()
        assert response["applicant_name"] == "John Doe"
        assert response["applicant_email"] == "john@example.com"
        assert response["state"] == "submitted"
        assert "created_at" in response or "createdAt" in response
