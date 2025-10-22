"""
Unit tests for AdoptionRequest edge cases and error scenarios.

This module tests edge cases, boundary conditions, and error handling
for the adoption request entity.
"""

from application.entity.adoption_request import AdoptionRequest


class TestAdoptionRequestEdgeCases:
    """Test suite for edge cases in adoption request."""

    def test_applicant_name_with_special_characters(self) -> None:
        """Test applicant name with special characters."""
        request = AdoptionRequest(
            applicant_name="Jean-Pierre O'Brien",
            applicant_email="jean@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.applicant_name == "Jean-Pierre O'Brien"

    def test_applicant_name_with_unicode(self) -> None:
        """Test applicant name with unicode characters."""
        request = AdoptionRequest(
            applicant_name="José García",
            applicant_email="jose@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.applicant_name == "José García"

    def test_applicant_name_with_whitespace_trimming(self) -> None:
        """Test that applicant name whitespace is trimmed."""
        request = AdoptionRequest(
            applicant_name="  John Doe  ",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.applicant_name == "John Doe"

    def test_email_with_subdomain(self) -> None:
        """Test email with subdomain."""
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@mail.example.co.uk",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.applicant_email == "john@mail.example.co.uk"

    def test_phone_with_various_formats(self) -> None:
        """Test phone with various formats."""
        phone_formats = [
            "555-1234",
            "(555) 123-4567",
            "+1-555-123-4567",
            "5551234567",
            "ext. 123",
        ]
        for phone in phone_formats:
            request = AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone=phone,
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
            )
            assert request.applicant_phone == phone

    def test_reason_with_maximum_length(self) -> None:
        """Test reason with maximum allowed length."""
        max_reason = "A" * 500
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption=max_reason,
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert len(request.reason_for_adoption) == 500

    def test_living_situation_with_maximum_length(self) -> None:
        """Test living situation with maximum allowed length."""
        max_situation = "B" * 500
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation=max_situation,
            experience_level="BEGINNER",
        )
        assert len(request.living_situation) == 500

    def test_family_size_boundary_values(self) -> None:
        """Test family size with boundary values."""
        # Minimum valid value
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.family_size == 1

        # Large family
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=100,
            living_situation="Test",
            experience_level="BEGINNER",
        )
        assert request.family_size == 100

    def test_has_other_pets_boolean_values(self) -> None:
        """Test has_other_pets with boolean values."""
        # True value
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            has_other_pets=True,
        )
        assert request.has_other_pets is True

        # False value
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            has_other_pets=False,
        )
        assert request.has_other_pets is False

    def test_approval_status_various_values(self) -> None:
        """Test approval status with various values."""
        statuses = ["pending", "approved", "rejected", "under_review"]
        for status in statuses:
            request = AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
                approval_status=status,
            )
            assert request.approval_status == status

    def test_review_notes_with_long_text(self) -> None:
        """Test review notes with long text."""
        long_notes = "This is a detailed review. " * 50
        request = AdoptionRequest(
            applicant_name="John Doe",
            applicant_email="john@example.com",
            applicant_phone="555-0000",
            reason_for_adoption="Test",
            family_size=1,
            living_situation="Test",
            experience_level="BEGINNER",
            review_notes=long_notes,
        )
        assert request.review_notes == long_notes

    def test_reviewer_id_format(self) -> None:
        """Test reviewer ID with various formats."""
        reviewer_ids = ["reviewer-123", "uuid-12345", "user@domain.com"]
        for reviewer_id in reviewer_ids:
            request = AdoptionRequest(
                applicant_name="John Doe",
                applicant_email="john@example.com",
                applicant_phone="555-0000",
                reason_for_adoption="Test",
                family_size=1,
                living_situation="Test",
                experience_level="BEGINNER",
                reviewer_id=reviewer_id,
            )
            assert request.reviewer_id == reviewer_id
