"""
Unit tests for Pet entity.

This module provides example unit tests for the Pet entity,
demonstrating how to test entity validation, methods, and functionality.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from application.entity.pet.version_1.pet import Pet, Category, Tag


class TestPetEntity:
    """Unit tests for Pet entity functionality."""

    def test_pet_creation_with_required_fields(self):
        """Test creating a Pet with only required fields."""
        pet = Pet(name="Buddy")

        assert pet.name == "Buddy"
        assert pet.pet_id is None
        assert pet.category is None
        assert pet.photo_urls == []
        assert pet.tags == []
        assert pet.status is None
        assert pet.data_source == "petstore_api"
        assert pet.created_at is not None
        assert pet.updated_at is None

    def test_pet_creation_with_all_fields(self):
        """Test creating a Pet with all fields populated."""
        category = Category(id=1, name="Dogs")
        tag1 = Tag(id=1, name="friendly")
        tag2 = Tag(id=2, name="large")

        pet = Pet(
            name="Max",
            pet_id=123,
            category=category,
            photo_urls=[
                "http://example.com/photo1.jpg",
                "http://example.com/photo2.jpg",
            ],
            tags=[tag1, tag2],
            status="available",
            data_source="custom_api",
        )

        assert pet.name == "Max"
        assert pet.pet_id == 123
        assert pet.category.name == "Dogs"
        assert pet.category.id == 1
        assert len(pet.photo_urls) == 2
        assert len(pet.tags) == 2
        assert pet.tags[0].name == "friendly"
        assert pet.tags[1].name == "large"
        assert pet.status == "available"
        assert pet.data_source == "custom_api"

    def test_pet_name_validation(self):
        """Test Pet name validation rules."""
        # Valid names
        pet1 = Pet(name="A")  # Minimum length
        assert pet1.name == "A"

        pet2 = Pet(name="  Buddy  ")  # Should be trimmed
        assert pet2.name == "Buddy"

        # Invalid names
        with pytest.raises(ValidationError) as exc_info:
            Pet(name="")
        assert "Pet name cannot be empty" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Pet(name="   ")  # Only whitespace
        assert "Pet name cannot be empty" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Pet(name="A" * 101)  # Too long
        assert "Pet name cannot exceed 100 characters" in str(exc_info.value)

    def test_pet_status_validation(self):
        """Test Pet status validation rules."""
        # Valid statuses
        for status in ["available", "pending", "sold"]:
            pet = Pet(name="Test", status=status)
            assert pet.status == status

        # None is allowed
        pet = Pet(name="Test", status=None)
        assert pet.status is None

        # Invalid status
        with pytest.raises(ValidationError) as exc_info:
            Pet(name="Test", status="invalid")
        assert "Status must be one of: ['available', 'pending', 'sold']" in str(
            exc_info.value
        )

    def test_timestamp_methods(self):
        """Test timestamp-related methods."""
        pet = Pet(name="Timestamp Test")

        # Initially no timestamps except created_at
        assert pet.created_at is not None
        assert pet.updated_at is None
        assert pet.load_timestamp is None
        assert pet.analysis_timestamp is None

        # Test update_timestamp
        pet.update_timestamp()
        assert pet.updated_at is not None

        # Test set_load_timestamp
        pet.set_load_timestamp()
        assert pet.load_timestamp is not None
        assert pet.updated_at is not None  # Should also update updated_at

        # Test set_analysis_timestamp
        pet.set_analysis_timestamp()
        assert pet.analysis_timestamp is not None

    def test_analysis_results_methods(self):
        """Test analysis results related methods."""
        pet = Pet(name="Analysis Test")

        # Initially no analysis
        assert not pet.is_analyzed()
        assert pet.analysis_results is None

        # Set analysis results
        results = {
            "total_pets": 100,
            "average_age": 3.5,
            "most_common_breed": "Labrador",
        }
        pet.set_analysis_results(results)

        assert pet.is_analyzed()
        assert pet.analysis_results == results
        assert pet.analysis_timestamp is not None

    def test_load_status_methods(self):
        """Test load status related methods."""
        pet = Pet(name="Load Test")

        # Initially not loaded
        assert not pet.is_loaded()
        assert pet.load_timestamp is None

        # Set load timestamp
        pet.set_load_timestamp()

        assert pet.is_loaded()
        assert pet.load_timestamp is not None

    def test_category_helper_methods(self):
        """Test category helper methods."""
        # Pet without category
        pet1 = Pet(name="No Category")
        assert pet1.get_category_name() == "Unknown"

        # Pet with category but no name
        pet2 = Pet(name="Empty Category", category=Category(id=1))
        assert pet2.get_category_name() == "Unknown"

        # Pet with category and name
        pet3 = Pet(name="With Category", category=Category(id=1, name="Dogs"))
        assert pet3.get_category_name() == "Dogs"

    def test_tag_helper_methods(self):
        """Test tag helper methods."""
        # Pet without tags
        pet1 = Pet(name="No Tags")
        assert pet1.get_tag_names() == []

        # Pet with tags (some without names)
        tags = [
            Tag(id=1, name="friendly"),
            Tag(id=2),  # No name
            Tag(id=3, name="large"),
            Tag(id=4, name=""),  # Empty name
        ]
        pet2 = Pet(name="With Tags", tags=tags)
        tag_names = pet2.get_tag_names()
        assert tag_names == ["friendly", "large"]

    def test_api_response_format(self):
        """Test API response format conversion."""
        category = Category(id=1, name="Dogs")
        tag = Tag(id=1, name="friendly")

        pet = Pet(
            name="API Test",
            pet_id=123,
            category=category,
            tags=[tag],
            status="available",
        )
        pet.state = "analyzed"  # Set a state for testing

        api_response = pet.to_api_response()

        # Check that aliases are used
        assert "petId" in api_response
        assert "photoUrls" in api_response
        assert "dataSource" in api_response
        assert "createdAt" in api_response
        assert api_response["petId"] == 123
        assert api_response["state"] == "analyzed"
        assert api_response["name"] == "API Test"

    def test_field_aliases(self):
        """Test that field aliases work correctly."""
        # Test creation with aliases
        pet_data = {
            "name": "Alias Test",
            "petId": 456,
            "photoUrls": ["http://example.com/photo.jpg"],
            "dataSource": "test_api",
            "createdAt": "2023-01-01T00:00:00Z",
            "updatedAt": "2023-01-02T00:00:00Z",
        }

        pet = Pet(**pet_data)

        assert pet.name == "Alias Test"
        assert pet.pet_id == 456
        assert pet.photo_urls == ["http://example.com/photo.jpg"]
        assert pet.data_source == "test_api"
        assert pet.created_at == "2023-01-01T00:00:00Z"
        assert pet.updated_at == "2023-01-02T00:00:00Z"

    def test_entity_constants(self):
        """Test entity constants are properly defined."""
        assert Pet.ENTITY_NAME == "Pet"
        assert Pet.ENTITY_VERSION == 1

    def test_model_configuration(self):
        """Test that model configuration allows extra fields."""
        # Should allow extra fields due to extra="allow"
        pet_data = {
            "name": "Config Test",
            "extra_field": "extra_value",
            "another_field": 123,
        }

        pet = Pet(**pet_data)
        assert pet.name == "Config Test"
        # Extra fields should be accessible
        assert hasattr(pet, "extra_field")
        assert pet.extra_field == "extra_value"  # type: ignore
