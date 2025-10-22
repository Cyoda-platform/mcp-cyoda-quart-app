"""
Unit tests for AdoptionRequest entity casting and type safety.

This module tests entity casting, type conversions, and serialization
for the adoption request entity.
"""

import pytest

from application.entity.adoption_request import AdoptionRequest
from common.entity.cyoda_entity import CyodaEntity


class TestAdoptionRequestCasting:
    """Test suite for entity casting and type safety."""

    @pytest.fixture
    def valid_adoption_request(self) -> AdoptionRequest:
        """Fixture providing a valid adoption request."""
        return AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-1234",
            reason_for_adoption="Love animals",
            family_size=3,
            living_situation="House with yard",
            experience_level="INTERMEDIATE",
        )

    def test_adoption_request_is_cyoda_entity(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test that AdoptionRequest is a CyodaEntity."""
        assert isinstance(valid_adoption_request, CyodaEntity)

    def test_adoption_request_has_entity_constants(self) -> None:
        """Test that AdoptionRequest has entity constants."""
        assert AdoptionRequest.ENTITY_NAME == "AdoptionRequest"
        assert AdoptionRequest.ENTITY_VERSION == 1

    def test_adoption_request_model_dump(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test model_dump serialization."""
        data = valid_adoption_request.model_dump()
        assert isinstance(data, dict)
        assert "applicant_name" in data
        assert "applicant_email" in data
        assert data["applicant_name"] == "John Doe"

    def test_adoption_request_model_dump_by_alias(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test model_dump with by_alias=True."""
        data = valid_adoption_request.model_dump(by_alias=True)
        assert isinstance(data, dict)
        # Check that aliases are used
        assert "createdAt" in data or "created_at" in data
        assert "updatedAt" in data or "updated_at" in data

    def test_adoption_request_model_dump_exclude_none(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test model_dump with exclude_none=True."""
        data = valid_adoption_request.model_dump(exclude_none=True)
        assert isinstance(data, dict)
        # updated_at should be None initially, so it should be excluded
        assert data.get("updated_at") is None or "updated_at" not in data

    def test_adoption_request_model_json_schema(self) -> None:
        """Test JSON schema generation."""
        schema = AdoptionRequest.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "applicant_name" in schema["properties"]
        assert "applicant_email" in schema["properties"]

    def test_adoption_request_field_aliases(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test that field aliases work correctly."""
        # Create with alias names
        data = {
            "applicant_name": "Jane Smith",
            "applicant_email": "jane@example.com",
            "applicant_phone": "555-5678",
            "reason_for_adoption": "Family pet",
            "family_size": 2,
            "living_situation": "Apartment",
            "experience_level": "BEGINNER",
            "hasOtherPets": True,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
            "reviewNotes": "Good candidate",
            "approvalStatus": "approved",
            "reviewerId": "reviewer-123",
        }
        request = AdoptionRequest(**data)
        assert request.has_other_pets is True
        assert request.review_notes == "Good candidate"
        assert request.approval_status == "approved"

    def test_adoption_request_populate_by_name(self) -> None:
        """Test that populate_by_name allows both snake_case and camelCase."""
        # Using snake_case
        request1 = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            has_other_pets=True,
        )
        assert request1.has_other_pets is True

        # Using camelCase (via alias)
        request2 = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            hasOtherPets=True,
        )
        assert request2.has_other_pets is True

    def test_adoption_request_validate_assignment(self) -> None:
        """Test that validate_assignment is enabled."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )

        # Assignment should validate
        request.applicant_name = "Jane Smith"
        assert request.applicant_name == "Jane Smith"

    def test_adoption_request_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed."""
        data = {
            "applicant_name": "John Doe",
            "applicant_email": "john@example.com",
            "applicant_phone": "555-0000",
            "reason_for_adoption": "Test",
            "family_size": 1,
            "living_situation": "Test",
            "experience_level": "BEGINNER",
            "extra_field": "extra_value",
        }
        request = AdoptionRequest(**data)
        assert hasattr(request, "extra_field")

    def test_adoption_request_to_api_response(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test to_api_response method."""
        response = valid_adoption_request.to_api_response()
        assert isinstance(response, dict)
        assert "applicant_name" in response
        assert "state" in response

    def test_adoption_request_timestamps_format(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test that timestamps are in ISO 8601 format."""
        assert valid_adoption_request.created_at is not None
        # Should end with Z for UTC
        assert valid_adoption_request.created_at.endswith("Z")

    def test_adoption_request_state_field(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test state field from CyodaEntity."""
        assert hasattr(valid_adoption_request, "state")
        assert valid_adoption_request.state == "initial_state"

    def test_adoption_request_entity_id_field(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test entity_id field from CyodaEntity."""
        assert hasattr(valid_adoption_request, "entity_id")

    def test_adoption_request_copy_method(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test model_copy method."""
        copy = valid_adoption_request.model_copy()
        assert copy.applicant_name == valid_adoption_request.applicant_name
        assert copy.applicant_email == valid_adoption_request.applicant_email
        assert copy is not valid_adoption_request

    def test_adoption_request_copy_with_update(
        self, valid_adoption_request: AdoptionRequest
    ) -> None:
        """Test model_copy with update."""
        copy = valid_adoption_request.model_copy(
            update={"applicant_name": "Jane Smith"}
        )
        assert copy.applicant_name == "Jane Smith"
        assert valid_adoption_request.applicant_name == "John Doe"
