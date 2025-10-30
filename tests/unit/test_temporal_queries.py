"""
Unit tests for temporal query and statistics features.

Tests the new point-in-time query, entity statistics, and change metadata
functionality added to CrudRepository, CyodaRepository, and EntityService.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.repository.cyoda.cyoda_repository import CyodaRepository
from common.service.entity_service import (
    EntityResponse,
    SearchConditionRequest,
)
from common.service.service import EntityServiceImpl


@pytest.fixture
def mock_auth_service():
    """Mock authentication service."""
    auth_service = MagicMock()
    auth_service.get_access_token = AsyncMock(return_value="mock_token")
    return auth_service


@pytest.fixture
def cyoda_repository(mock_auth_service):
    """Create CyodaRepository instance with mocked auth service."""
    # Reset singleton for testing
    CyodaRepository._instance = None
    return CyodaRepository(mock_auth_service)


@pytest.fixture
def entity_service(cyoda_repository):
    """Create EntityServiceImpl instance with mocked repository."""
    # Reset singleton for testing
    EntityServiceImpl._instance = None
    return EntityServiceImpl(cyoda_repository)


@pytest.fixture
def sample_entity_data():
    """Sample entity data for testing."""
    return {
        "technical_id": "test-entity-123",
        "name": "Test Entity",
        "description": "Test description",
        "current_state": "VALIDATED",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def point_in_time():
    """Sample point in time for temporal queries."""
    return datetime(2024, 1, 1, 12, 0, 0)


class TestCyodaRepositoryTemporalQueries:
    """Test temporal query features in CyodaRepository."""

    @pytest.mark.asyncio
    async def test_find_by_id_with_point_in_time(
        self, cyoda_repository, sample_entity_data, point_in_time
    ):
        """Test finding entity by ID at a specific point in time."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            # The response should have data and meta structure
            mock_request.return_value = {
                "status": 200,
                "json": {
                    "data": sample_entity_data,
                    "meta": {"state": "VALIDATED"},
                },
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            result = await cyoda_repository.find_by_id(
                meta, "test-entity-123", point_in_time
            )

            assert result is not None
            assert result["technical_id"] == "test-entity-123"
            assert result["current_state"] == "VALIDATED"

            # Verify the request included point_in_time parameter
            call_args = mock_request.call_args
            assert "pointInTime" in str(call_args)

    @pytest.mark.asyncio
    async def test_find_by_id_without_point_in_time(
        self, cyoda_repository, sample_entity_data
    ):
        """Test finding entity by ID without point in time (current state)."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 200,
                "json": {
                    "data": sample_entity_data,
                    "meta": {"state": "VALIDATED"},
                },
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            result = await cyoda_repository.find_by_id(meta, "test-entity-123")

            assert result is not None
            # Verify no point_in_time parameter in request
            call_args = mock_request.call_args
            assert "pointInTime" not in str(call_args)

    @pytest.mark.asyncio
    async def test_find_all_by_criteria_with_point_in_time(
        self, cyoda_repository, sample_entity_data, point_in_time
    ):
        """Test searching entities with criteria at a specific point in time."""
        with patch(
            "common.repository.cyoda.cyoda_repository.CyodaRepository._send_search_request",
            new_callable=AsyncMock,
        ) as mock_search:
            mock_search.return_value = {
                "status": 200,
                "json": [sample_entity_data],
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            criteria = {"name": "Test Entity"}
            results = await cyoda_repository.find_all_by_criteria(
                meta, criteria, point_in_time
            )

            assert len(results) == 1
            assert results[0]["technical_id"] == "test-entity-123"

            # Verify point_in_time was included in the search
            call_args = mock_search.call_args
            assert point_in_time in call_args[0] or "pointInTime" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_entity_count(self, cyoda_repository, point_in_time):
        """Test getting entity count with optional point in time."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 200,
                "json": {"count": 42},
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            count = await cyoda_repository.get_entity_count(meta, point_in_time)

            assert count == 42
            # Verify the request was made to the stats endpoint
            call_args = mock_request.call_args
            assert "entity/stats" in str(call_args)
            assert "pointInTime" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_entity_count_without_point_in_time(self, cyoda_repository):
        """Test getting current entity count."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 200,
                "json": {"count": 100},
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            count = await cyoda_repository.get_entity_count(meta)

            assert count == 100

    @pytest.mark.asyncio
    async def test_get_entity_count_with_list_response(self, cyoda_repository):
        """Test getting entity count when response is a list (by state)."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 200,
                "json": [
                    {"state": "VALIDATED", "count": 30},
                    {"state": "DRAFT", "count": 20},
                ],
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            count = await cyoda_repository.get_entity_count(meta)

            assert count == 50  # Sum of all counts

    @pytest.mark.asyncio
    async def test_get_entity_count_error_handling(self, cyoda_repository):
        """Test entity count error handling."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 500,
                "json": {"error": "Internal server error"},
            }

            meta = {"entity_model": "TestEntity", "entity_version": "1"}
            count = await cyoda_repository.get_entity_count(meta)

            assert count == 0  # Should return 0 on error

    @pytest.mark.asyncio
    async def test_get_entity_changes_metadata(self, cyoda_repository, point_in_time):
        """Test getting entity change history metadata."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_changes = [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "user": "user1",
                    "action": "CREATE",
                },
                {
                    "timestamp": "2024-01-01T11:00:00Z",
                    "user": "user2",
                    "action": "UPDATE",
                },
            ]
            mock_request.return_value = {
                "status": 200,
                "json": mock_changes,
            }

            changes = await cyoda_repository.get_entity_changes_metadata(
                "test-entity-123", point_in_time
            )

            assert len(changes) == 2
            assert changes[0]["action"] == "CREATE"
            assert changes[1]["action"] == "UPDATE"

            # Verify the request was made to the changes endpoint
            call_args = mock_request.call_args
            assert "entity/test-entity-123/changes" in str(call_args)
            assert "pointInTime" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_entity_changes_metadata_error_handling(self, cyoda_repository):
        """Test entity changes metadata error handling."""
        with patch(
            "common.repository.cyoda.cyoda_repository.send_cyoda_request",
            new_callable=AsyncMock,
        ) as mock_request:
            mock_request.return_value = {
                "status": 404,
                "json": {"error": "Entity not found"},
            }

            changes = await cyoda_repository.get_entity_changes_metadata(
                "non-existent-id"
            )

            assert changes == []  # Should return empty list on error


class TestEntityServiceTemporalQueries:
    """Test temporal query features in EntityService."""

    @pytest.mark.asyncio
    async def test_get_by_id_at_time(
        self, entity_service, sample_entity_data, point_in_time
    ):
        """Test getting entity by ID at a specific point in time."""
        with patch.object(
            entity_service._repository, "find_by_id", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = sample_entity_data

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                result = await entity_service.get_by_id_at_time(
                    "test-entity-123", "TestEntity", point_in_time
                )

                assert result is not None
                assert isinstance(result, EntityResponse)
                assert result.metadata.id == "test-entity-123"

                # Verify find_by_id was called with point_in_time
                mock_find.assert_called_once()
                call_args = mock_find.call_args
                assert call_args.args[2] == point_in_time

    @pytest.mark.asyncio
    async def test_get_by_id_at_time_not_found(self, entity_service, point_in_time):
        """Test getting non-existent entity at a point in time."""
        with patch.object(
            entity_service._repository, "find_by_id", new_callable=AsyncMock
        ) as mock_find:
            mock_find.return_value = None

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                result = await entity_service.get_by_id_at_time(
                    "non-existent-id", "TestEntity", point_in_time
                )

                assert result is None

    @pytest.mark.asyncio
    async def test_search_at_time(
        self, entity_service, sample_entity_data, point_in_time
    ):
        """Test searching entities at a specific point in time."""
        with patch.object(
            entity_service._repository, "find_all_by_criteria", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [sample_entity_data]

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                condition = (
                    SearchConditionRequest.builder().equals("name", "Test").build()
                )
                results = await entity_service.search_at_time(
                    "TestEntity", condition, point_in_time
                )

                assert len(results) == 1
                assert isinstance(results[0], EntityResponse)

                # Verify find_all_by_criteria was called with point_in_time
                mock_search.assert_called_once()
                call_args = mock_search.call_args
                assert call_args.args[2] == point_in_time

    @pytest.mark.asyncio
    async def test_get_entity_count(self, entity_service, point_in_time):
        """Test getting entity count with point in time."""
        with patch.object(
            entity_service._repository, "get_entity_count", new_callable=AsyncMock
        ) as mock_count:
            mock_count.return_value = 42

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                count = await entity_service.get_entity_count(
                    "TestEntity", "1", point_in_time
                )

                assert count == 42
                mock_count.assert_called_once()
                call_args = mock_count.call_args
                assert call_args.args[1] == point_in_time

    @pytest.mark.asyncio
    async def test_get_entity_count_without_point_in_time(self, entity_service):
        """Test getting current entity count."""
        with patch.object(
            entity_service._repository, "get_entity_count", new_callable=AsyncMock
        ) as mock_count:
            mock_count.return_value = 100

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                count = await entity_service.get_entity_count("TestEntity")

                assert count == 100
                mock_count.assert_called_once()
                call_args = mock_count.call_args
                assert call_args.args[1] is None

    @pytest.mark.asyncio
    async def test_get_entity_count_error_handling(self, entity_service):
        """Test entity count error handling."""
        with patch.object(
            entity_service._repository, "get_entity_count", new_callable=AsyncMock
        ) as mock_count:
            mock_count.side_effect = Exception("Database error")

            with patch.object(
                entity_service._repository, "get_meta", new_callable=AsyncMock
            ) as mock_meta:
                mock_meta.return_value = {
                    "entity_model": "TestEntity",
                    "entity_version": "1",
                }

                count = await entity_service.get_entity_count("TestEntity")

                assert count == 0  # Should return 0 on error

    @pytest.mark.asyncio
    async def test_get_entity_changes_metadata(self, entity_service, point_in_time):
        """Test getting entity change history metadata."""
        mock_changes = [
            {"timestamp": "2024-01-01T10:00:00Z", "action": "CREATE"},
            {"timestamp": "2024-01-01T11:00:00Z", "action": "UPDATE"},
        ]

        with patch.object(
            entity_service._repository,
            "get_entity_changes_metadata",
            new_callable=AsyncMock,
        ) as mock_changes_method:
            mock_changes_method.return_value = mock_changes

            changes = await entity_service.get_entity_changes_metadata(
                "test-entity-123", "TestEntity", "1", point_in_time
            )

            assert len(changes) == 2
            assert changes[0]["action"] == "CREATE"
            assert changes[1]["action"] == "UPDATE"

            mock_changes_method.assert_called_once()
            call_args = mock_changes_method.call_args
            assert call_args.args[0] == "test-entity-123"
            assert call_args.args[1] == point_in_time

    @pytest.mark.asyncio
    async def test_get_entity_changes_metadata_error_handling(self, entity_service):
        """Test entity changes metadata error handling."""
        with patch.object(
            entity_service._repository,
            "get_entity_changes_metadata",
            new_callable=AsyncMock,
        ) as mock_changes:
            mock_changes.side_effect = Exception("API error")

            changes = await entity_service.get_entity_changes_metadata(
                "test-entity-123", "TestEntity"
            )

            assert changes == []  # Should return empty list on error
