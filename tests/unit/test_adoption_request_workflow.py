"""
Unit tests for AdoptionRequest workflow integration.

This module tests the complete workflow of an adoption request from creation
through validation, processing, and approval.
"""

import pytest

from application.entity.adoption_request import AdoptionRequest
from application.processor.adoption_request_processor import AdoptionRequestProcessor
from application.criterion.adoption_request_criterion import (
    AdoptionRequestValidationCriterion,
)


class TestAdoptionRequestWorkflowIntegration:
    """Test suite for complete adoption request workflow."""

    @pytest.fixture
    def valid_request_data(self) -> dict:
        """Fixture providing valid adoption request data."""
        return {
            "applicant_name": "John Doe",
            "applicant_email": "john@example.com",
            "applicant_phone": "555-1234",
            "reason_for_adoption": "Love animals and want to provide a home",
            "family_size": 3,
            "living_situation": "House with large yard",
            "experience_level": "INTERMEDIATE",
        }

    def test_create_adoption_request(self, valid_request_data: dict) -> None:
        """Test creating an adoption request."""
        request = AdoptionRequest(**valid_request_data)
        assert request.applicant_name == "John Doe"
        assert request.state == "initial_state"

    @pytest.mark.asyncio
    async def test_validate_adoption_request(self, valid_request_data: dict) -> None:
        """Test validating an adoption request."""
        request = AdoptionRequest(**valid_request_data)
        criterion = AdoptionRequestValidationCriterion()
        result = await criterion.check(request)
        assert result is True

    @pytest.mark.asyncio
    async def test_process_adoption_request(self, valid_request_data: dict) -> None:
        """Test processing an adoption request."""
        request = AdoptionRequest(**valid_request_data)
        processor = AdoptionRequestProcessor()
        await processor.process(request)
        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_workflow_state_transitions(self, valid_request_data: dict) -> None:
        """Test state transitions through workflow."""
        request = AdoptionRequest(**valid_request_data)
        assert request.state == "initial_state"

        # Simulate state transition to submitted
        request.state = "submitted"
        assert request.state == "submitted"

        # Verify request is ready for review
        assert request.is_ready_for_review() is True

    @pytest.mark.asyncio
    async def test_workflow_approval_flow(self, valid_request_data: dict) -> None:
        """Test approval flow through workflow."""
        request = AdoptionRequest(**valid_request_data)

        # Set approval status
        request.set_approval_status("approved", "reviewer-123")
        assert request.is_approved() is True
        assert request.reviewer_id == "reviewer-123"

    @pytest.mark.asyncio
    async def test_workflow_rejection_flow(self, valid_request_data: dict) -> None:
        """Test rejection flow through workflow."""
        request = AdoptionRequest(**valid_request_data)

        # Set rejection status
        request.set_approval_status("rejected", "reviewer-456")
        assert request.is_approved() is False
        assert request.approval_status == "rejected"

    @pytest.mark.asyncio
    async def test_workflow_with_review_notes(self, valid_request_data: dict) -> None:
        """Test workflow with review notes."""
        request = AdoptionRequest(**valid_request_data)

        # Add review notes
        request.set_review_notes("Excellent candidate with good experience")
        assert request.review_notes == "Excellent candidate with good experience"
        assert request.updated_at is not None

    @pytest.mark.asyncio
    async def test_workflow_multiple_updates(self, valid_request_data: dict) -> None:
        """Test multiple updates in workflow."""
        request = AdoptionRequest(**valid_request_data)
        original_created_at = request.created_at

        # First update
        request.set_review_notes("Initial review")
        first_updated_at = request.updated_at

        # Second update
        request.set_approval_status("approved", "reviewer-789")
        second_updated_at = request.updated_at

        # Verify timestamps
        assert request.created_at == original_created_at
        assert first_updated_at is not None
        assert second_updated_at is not None
        assert second_updated_at != first_updated_at

    @pytest.mark.asyncio
    async def test_workflow_validation_before_approval(
        self, valid_request_data: dict
    ) -> None:
        """Test validation before approval in workflow."""
        request = AdoptionRequest(**valid_request_data)
        criterion = AdoptionRequestValidationCriterion()

        # Validate before approval
        is_valid = await criterion.check(request)
        assert is_valid is True

        # Approve after validation
        request.set_approval_status("approved", "reviewer-999")
        assert request.is_approved() is True

    @pytest.mark.asyncio
    async def test_workflow_with_optional_fields(self) -> None:
        """Test workflow with optional fields."""
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

    @pytest.mark.asyncio
    async def test_workflow_api_response_format(self, valid_request_data: dict) -> None:
        """Test API response format from workflow."""
        request = AdoptionRequest(**valid_request_data, state="submitted")
        response = request.to_api_response()

        assert "applicant_name" in response
        assert "applicant_email" in response
        assert "state" in response
        assert response["state"] == "submitted"
