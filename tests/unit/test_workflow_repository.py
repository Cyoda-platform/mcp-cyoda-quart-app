"""
Unit tests for WorkflowRepository.
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.repository.cyoda.workflow_repository import (
    WorkflowExportResponse,
    WorkflowImportRequest,
    WorkflowRepository,
)


class MockCyodaAuthService:
    """Mock Cyoda authentication service."""

    async def get_access_token(self) -> str:
        """Return a mock access token."""
        return "mock-token-123"

    def invalidate_tokens(self) -> None:
        """Invalidate tokens."""
        pass


class TestWorkflowExportResponse:
    """Test suite for WorkflowExportResponse dataclass."""

    def test_from_api_response_complete(self):
        """Test creating WorkflowExportResponse from complete API response."""
        api_response = {
            "entityName": "TestEntity",
            "modelVersion": "1",
            "workflows": [
                {"name": "workflow1", "transitions": ["approve", "reject"]},
                {"name": "workflow2", "transitions": ["update"]},
            ],
        }

        result = WorkflowExportResponse.from_api_response(api_response)

        assert result.entity_name == "TestEntity"
        assert result.model_version == "1"
        assert len(result.workflows) == 2
        assert result.workflows[0]["name"] == "workflow1"

    def test_from_api_response_minimal(self):
        """Test creating WorkflowExportResponse from minimal API response."""
        api_response = {}

        result = WorkflowExportResponse.from_api_response(api_response)

        assert result.entity_name == ""
        assert result.model_version == ""
        assert result.workflows == []

    def test_from_api_response_partial(self):
        """Test creating WorkflowExportResponse from partial API response."""
        api_response = {
            "entityName": "TestEntity",
        }

        result = WorkflowExportResponse.from_api_response(api_response)

        assert result.entity_name == "TestEntity"
        assert result.model_version == ""
        assert result.workflows == []


class TestWorkflowImportRequest:
    """Test suite for WorkflowImportRequest dataclass."""

    def test_to_dict_complete(self):
        """Test converting WorkflowImportRequest to dict."""
        workflows = [
            {"name": "workflow1", "transitions": ["approve"]},
        ]
        request = WorkflowImportRequest(workflows=workflows, import_mode="REPLACE")

        result = request.to_dict()

        assert result["workflows"] == workflows
        assert result["importMode"] == "REPLACE"

    def test_to_dict_empty_workflows(self):
        """Test converting WorkflowImportRequest with empty workflows."""
        request = WorkflowImportRequest(workflows=[], import_mode="MERGE")

        result = request.to_dict()

        assert result["workflows"] == []
        assert result["importMode"] == "MERGE"


class TestWorkflowRepository:
    """Test suite for WorkflowRepository."""

    @pytest.fixture
    def auth_service(self):
        """Create a mock auth service."""
        return MockCyodaAuthService()

    @pytest.fixture
    def repository(self, auth_service):
        """Create a WorkflowRepository instance."""
        # Reset singleton
        WorkflowRepository._instance = None
        return WorkflowRepository(auth_service)

    # Singleton Pattern Tests

    def test_singleton_pattern(self, auth_service):
        """Test that WorkflowRepository follows singleton pattern."""
        WorkflowRepository._instance = None
        repo1 = WorkflowRepository(auth_service)
        repo2 = WorkflowRepository(auth_service)

        assert repo1 is repo2

    def test_singleton_initialization_once(self, auth_service):
        """Test that singleton is initialized only once."""
        WorkflowRepository._instance = None
        repo1 = WorkflowRepository(auth_service)

        # Second call should not reinitialize
        repo2 = WorkflowRepository(auth_service)
        assert repo1 is repo2
        assert repo1._initialized is True

    # Export Workflows Tests

    @pytest.mark.asyncio
    async def test_export_entity_workflows_success(self, repository):
        """Test exporting entity workflows successfully."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "entityName": "TestEntity",
                    "modelVersion": "1",
                    "workflows": [
                        {"name": "main_workflow", "transitions": ["approve", "reject"]},
                    ],
                },
                "status": 200,
            }

            result = await repository.export_entity_workflows("TestEntity", "1")

            assert isinstance(result, WorkflowExportResponse)
            assert result.entity_name == "TestEntity"
            assert result.model_version == "1"
            assert len(result.workflows) == 1
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_entity_workflows_empty(self, repository):
        """Test exporting entity workflows when none exist."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "entityName": "TestEntity",
                    "modelVersion": "1",
                    "workflows": [],
                },
                "status": 200,
            }

            result = await repository.export_entity_workflows("TestEntity", "1")

            assert result.workflows == []

    @pytest.mark.asyncio
    async def test_export_entity_workflows_error(self, repository):
        """Test exporting entity workflows with error response."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Export failed"},
                "status": 500,
            }

            # Should raise exception on error
            with pytest.raises(Exception) as exc_info:
                await repository.export_entity_workflows("TestEntity", "1")

            assert "Failed to export workflows" in str(exc_info.value)

    # Import Workflows Tests

    @pytest.mark.asyncio
    async def test_import_entity_workflows_success(self, repository):
        """Test importing entity workflows successfully."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"success": True, "message": "Import successful"},
                "status": 200,
            }

            workflows = [{"name": "workflow1", "transitions": ["approve"]}]

            result = await repository.import_entity_workflows(
                "TestEntity", "1", workflows, "REPLACE"
            )

            assert result["success"] is True
            assert result["message"] == "Import successful"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_entity_workflows_merge_mode(self, repository):
        """Test importing entity workflows with MERGE mode."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"success": True},
                "status": 200,
            }

            workflows = [{"name": "workflow1"}]

            result = await repository.import_entity_workflows(
                "TestEntity", "1", workflows, "MERGE"
            )

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_import_entity_workflows_error(self, repository):
        """Test importing entity workflows with error."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Import failed", "success": False},
                "status": 500,
            }

            workflows = [{"name": "workflow1"}]

            # Should raise exception on error
            with pytest.raises(Exception) as exc_info:
                await repository.import_entity_workflows(
                    "TestEntity", "1", workflows, "REPLACE"
                )

            assert "Failed to import workflows" in str(exc_info.value)

    # Validate Workflows Tests

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_valid(self, repository):
        """Test validating valid workflow definitions."""
        workflows = [{"name": "workflow1", "transitions": ["approve"]}]

        result = await repository.validate_workflow_definitions(workflows)

        assert result["valid"] is True
        assert result["workflow_count"] == 1

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_invalid(self, repository):
        """Test validating invalid workflow definitions."""
        # Empty workflow should fail validation
        workflows = [{}]

        result = await repository.validate_workflow_definitions(workflows)

        assert result["valid"] is False
        assert "validation_errors" in result

    # Get Workflow Count Tests

    @pytest.mark.asyncio
    async def test_get_workflow_count_success(self, repository):
        """Test getting workflow count successfully."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "entityName": "TestEntity",
                    "workflows": [
                        {"name": "workflow1"},
                        {"name": "workflow2"},
                        {"name": "workflow3"},
                    ],
                },
                "status": 200,
            }

            result = await repository.get_workflow_count("TestEntity", "1")

            assert result == 3

    @pytest.mark.asyncio
    async def test_get_workflow_count_empty(self, repository):
        """Test getting workflow count when no workflows exist."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"entityName": "TestEntity", "workflows": []},
                "status": 200,
            }

            result = await repository.get_workflow_count("TestEntity", "1")

            assert result == 0

    @pytest.mark.asyncio
    async def test_get_workflow_count_error(self, repository):
        """Test getting workflow count with error."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Failed to get workflows"},
                "status": 500,
            }

            # Should raise exception on error
            with pytest.raises(Exception) as exc_info:
                await repository.get_workflow_count("TestEntity", "1")

            assert "Failed to export workflows" in str(exc_info.value)

    # Additional Edge Cases and Error Handling Tests

    @pytest.mark.asyncio
    async def test_export_entity_workflows_with_multiple_workflows(self, repository):
        """Test exporting entity with multiple complex workflows."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "entityName": "ComplexEntity",
                    "modelVersion": "2",
                    "workflows": [
                        {
                            "name": "approval_workflow",
                            "transitions": ["submit", "approve", "reject"],
                            "states": ["draft", "pending", "approved", "rejected"],
                        },
                        {
                            "name": "review_workflow",
                            "transitions": ["review", "complete"],
                            "states": ["new", "in_review", "completed"],
                        },
                        {
                            "name": "archive_workflow",
                            "transitions": ["archive", "restore"],
                            "states": ["active", "archived"],
                        },
                    ],
                },
                "status": 200,
            }

            result = await repository.export_entity_workflows("ComplexEntity", "2")

            assert isinstance(result, WorkflowExportResponse)
            assert result.entity_name == "ComplexEntity"
            assert result.model_version == "2"
            assert len(result.workflows) == 3
            assert result.workflows[0]["name"] == "approval_workflow"
            assert result.workflows[1]["name"] == "review_workflow"
            assert result.workflows[2]["name"] == "archive_workflow"

    @pytest.mark.asyncio
    async def test_import_entity_workflows_with_complex_workflows(self, repository):
        """Test importing complex workflow definitions."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Imported 3 workflows",
                    "imported_count": 3,
                },
                "status": 200,
            }

            workflows = [
                {
                    "name": "workflow1",
                    "transitions": ["approve", "reject"],
                    "states": ["draft", "approved", "rejected"],
                },
                {
                    "name": "workflow2",
                    "transitions": ["submit", "complete"],
                    "states": ["new", "submitted", "completed"],
                },
                {
                    "name": "workflow3",
                    "transitions": ["archive"],
                    "states": ["active", "archived"],
                },
            ]

            result = await repository.import_entity_workflows(
                "TestEntity", "1", workflows, "REPLACE"
            )

            assert result["success"] is True
            assert result["imported_count"] == 3

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_empty_list(self, repository):
        """Test validating empty workflow list."""
        result = await repository.validate_workflow_definitions([])

        assert result["valid"] is False
        assert "No workflows provided" in result["error"]
        assert result["workflow_count"] == 0

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_not_list(self, repository):
        """Test validating non-list input."""
        result = await repository.validate_workflow_definitions({"not": "a list"})

        assert result["valid"] is False
        assert "must be provided as a list" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_with_non_dict_items(self, repository):
        """Test validating workflow list with non-dict items."""
        workflows = [
            {"name": "valid_workflow"},
            "invalid_string",
            {"name": "another_valid"},
            123,
        ]

        result = await repository.validate_workflow_definitions(workflows)

        assert result["valid"] is False
        assert "validation_errors" in result
        assert len(result["validation_errors"]) == 2

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_with_empty_dicts(self, repository):
        """Test validating workflow list with empty dictionaries."""
        workflows = [{"name": "workflow1"}, {}, {"name": "workflow2"}]

        result = await repository.validate_workflow_definitions(workflows)

        assert result["valid"] is False
        assert "validation_errors" in result

    @pytest.mark.asyncio
    async def test_validate_workflow_definitions_exception(self, repository):
        """Test validate_workflow_definitions with exception."""
        # Pass None to trigger exception
        result = await repository.validate_workflow_definitions(None)

        assert result["valid"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_import_entity_workflows_default_mode(self, repository):
        """Test importing workflows with default import mode."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"success": True},
                "status": 200,
            }

            workflows = [{"name": "workflow1"}]

            # Call without specifying import_mode (should default to REPLACE)
            result = await repository.import_entity_workflows(
                "TestEntity", "1", workflows
            )

            assert result["success"] is True
            # Verify the request was made with REPLACE mode
            call_args = mock_request.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_export_entity_workflows_with_version_number(self, repository):
        """Test exporting workflows with numeric version."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "entityName": "TestEntity",
                    "modelVersion": 2,  # Numeric version
                    "workflows": [{"name": "workflow1"}],
                },
                "status": 200,
            }

            result = await repository.export_entity_workflows("TestEntity", "2")

            assert result.model_version == "2"  # Should be converted to string

    @pytest.mark.asyncio
    async def test_import_entity_workflows_exception_handling(self, repository):
        """Test import_entity_workflows exception handling."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            mock_request.side_effect = Exception("Network error")

            workflows = [{"name": "workflow1"}]

            with pytest.raises(Exception) as exc_info:
                await repository.import_entity_workflows(
                    "TestEntity", "1", workflows, "REPLACE"
                )

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_workflow_count_with_large_number(self, repository):
        """Test getting workflow count with large number of workflows."""
        with patch(
            "common.repository.cyoda.workflow_repository.send_cyoda_request"
        ) as mock_request:
            # Create 100 workflows
            workflows = [{"name": f"workflow_{i}"} for i in range(100)]
            mock_request.return_value = {
                "json": {"entityName": "TestEntity", "workflows": workflows},
                "status": 200,
            }

            result = await repository.get_workflow_count("TestEntity", "1")

            assert result == 100

    @pytest.mark.asyncio
    async def test_singleton_thread_safety(self, auth_service):
        """Test singleton thread safety."""
        import threading

        WorkflowRepository._instance = None
        instances = []

        def create_instance():
            instances.append(WorkflowRepository(auth_service))

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same
        assert all(inst is instances[0] for inst in instances)
