"""
Unit tests for DeploymentRepository.
"""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.repository.cyoda.deployment_repository import (
    DeploymentRequest,
    DeploymentResponse,
    DeploymentRepository,
)


class MockCyodaAuthService:
    """Mock Cyoda authentication service."""

    async def get_access_token(self) -> str:
        """Return a mock access token."""
        return "mock-token-123"

    def invalidate_tokens(self) -> None:
        """Invalidate tokens."""
        pass


class TestDeploymentDataclasses:
    """Test suite for Deployment dataclasses."""

    def test_deployment_request_to_dict_minimal(self):
        """Test converting DeploymentRequest to dict with minimal data."""
        request = DeploymentRequest(technical_id="tech-123")

        result = request.to_dict()

        assert result["technical_id"] == "tech-123"
        assert result["entity"] is None
        assert "params" not in result

    def test_deployment_request_to_dict_complete(self):
        """Test converting DeploymentRequest to dict with all data."""
        entity_data = {"name": "test", "version": "1.0"}
        params = {"param1": "value1"}
        request = DeploymentRequest(
            technical_id="tech-123",
            user_id="user-456",
            entity_data=entity_data,
            params=params,
        )

        result = request.to_dict()

        assert result["technical_id"] == "tech-123"
        assert result["entity"] == entity_data
        assert result["params"] == params

    def test_deployment_response_from_api_response_complete(self):
        """Test creating DeploymentResponse from complete API response."""
        api_response = {
            "success": True,
            "message": "Deployment successful",
            "build_id": "build-123",
            "status": "completed",
            "data": {"key": "value"},
        }

        result = DeploymentResponse.from_api_response(api_response)

        assert result.success is True
        assert result.message == "Deployment successful"
        assert result.build_id == "build-123"
        assert result.status == "completed"
        assert result.data == {"key": "value"}

    def test_deployment_response_from_api_response_minimal(self):
        """Test creating DeploymentResponse from minimal API response."""
        api_response = {}

        result = DeploymentResponse.from_api_response(api_response)

        assert result.success is False
        assert result.message == ""
        assert result.build_id is None
        assert result.status is None
        # data defaults to {} when not provided
        assert result.data == {}


class TestDeploymentRepository:
    """Test suite for DeploymentRepository."""

    @pytest.fixture
    def auth_service(self):
        """Create a mock auth service."""
        return MockCyodaAuthService()

    @pytest.fixture
    def repository(self, auth_service):
        """Create a DeploymentRepository instance."""
        # Reset singleton
        DeploymentRepository._instance = None
        return DeploymentRepository(auth_service)

    # Singleton Pattern Tests

    def test_singleton_pattern(self, auth_service):
        """Test that DeploymentRepository follows singleton pattern."""
        DeploymentRepository._instance = None
        repo1 = DeploymentRepository(auth_service)
        repo2 = DeploymentRepository(auth_service)

        assert repo1 is repo2

    # Schedule Deploy Env Tests

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_success(self, repository):
        """Test scheduling environment deployment successfully."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Environment deployment scheduled",
                    "build_id": "build-123",
                },
                "status": 200,
            }

            result = await repository.schedule_deploy_env("env-tech-123")

            assert isinstance(result, DeploymentResponse)
            assert result.success is True
            assert result.message == "Environment deployment scheduled"
            assert result.build_id == "build-123"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_error(self, repository):
        """Test scheduling environment deployment with error."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Deployment failed"},
                "status": 500,
            }

            with pytest.raises(Exception) as exc_info:
                await repository.schedule_deploy_env("env-tech-123")

            assert "Failed to schedule environment deployment" in str(exc_info.value)

    # Schedule Build User Application Tests

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_success(self, repository):
        """Test scheduling user application build successfully."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Build scheduled",
                    "build_id": "build-456",
                },
                "status": 200,
            }

            result = await repository.schedule_build_user_application(
                "app-tech-123", user_id="user-1", entity_data={"version": "1.0"}
            )

            assert isinstance(result, DeploymentResponse)
            assert result.success is True
            assert result.build_id == "build-456"

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_minimal(self, repository):
        """Test scheduling user application build with minimal parameters."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Build scheduled",
                },
                "status": 200,
            }

            result = await repository.schedule_build_user_application("app-tech-123")

            assert isinstance(result, DeploymentResponse)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_error(self, repository):
        """Test scheduling user application build with error."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Build failed"},
                "status": 500,
            }

            with pytest.raises(Exception) as exc_info:
                await repository.schedule_build_user_application("app-tech-123")

            assert "Failed to schedule user application build" in str(exc_info.value)

    # Schedule Deploy User Application Tests

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_success(self, repository):
        """Test scheduling user application deployment successfully."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Deployment scheduled",
                    "build_id": "build-789",
                },
                "status": 200,
            }

            result = await repository.schedule_deploy_user_application(
                "app-tech-123", user_id="user-1", entity_data={"version": "1.0"}
            )

            assert isinstance(result, DeploymentResponse)
            assert result.success is True
            assert result.build_id == "build-789"

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_minimal(self, repository):
        """Test scheduling user application deployment with minimal parameters."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Deployment scheduled",
                },
                "status": 200,
            }

            result = await repository.schedule_deploy_user_application("app-tech-123")

            assert isinstance(result, DeploymentResponse)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_error(self, repository):
        """Test scheduling user application deployment with error."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Deployment failed"},
                "status": 500,
            }

            with pytest.raises(Exception) as exc_info:
                await repository.schedule_deploy_user_application("app-tech-123")

            assert "Failed to schedule user application deployment" in str(
                exc_info.value
            )

    # Get Env Deploy Status Tests

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_success(self, repository):
        """Test getting deployment status successfully."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Status retrieved",
                    "build_id": "build-123",
                    "status": "completed",
                    "data": {"progress": 100},
                },
                "status": 200,
            }

            result = await repository.get_env_deploy_status("build-123")

            assert isinstance(result, DeploymentResponse)
            assert result.success is True
            assert result.status == "completed"
            assert result.data == {"progress": 100}

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_with_user_id(self, repository):
        """Test getting deployment status with user ID."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Status retrieved",
                    "status": "in_progress",
                },
                "status": 200,
            }

            result = await repository.get_env_deploy_status(
                "build-123", user_id="user-1"
            )

            assert isinstance(result, DeploymentResponse)
            assert result.success is True
            assert result.status == "in_progress"

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_error(self, repository):
        """Test getting deployment status with error."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"errorMessage": "Status check failed"},
                "status": 500,
            }

            with pytest.raises(Exception) as exc_info:
                await repository.get_env_deploy_status("build-123")

            assert "Failed to get deployment status" in str(exc_info.value)

    # Additional Edge Cases and Error Handling Tests

    @pytest.mark.asyncio
    async def test_send_ai_host_request_with_401_retry(self, repository):
        """Test _send_ai_host_request with 401 retry logic."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            # First call returns 401, second call succeeds
            mock_request.side_effect = [
                {"json": {"errorMessage": "Unauthorized"}, "status": 401},
                {"json": {"success": True}, "status": 200},
            ]

            result = await repository._send_ai_host_request(
                method="get", path="test/path"
            )

            assert result["status"] == 200
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_send_ai_host_request_with_exception_401_retry(self, repository):
        """Test _send_ai_host_request with exception containing 401."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            # First call raises exception with 401, second call succeeds
            mock_request.side_effect = [
                Exception("401 Unauthorized"),
                {"json": {"success": True}, "status": 200},
            ]

            result = await repository._send_ai_host_request(
                method="get", path="test/path"
            )

            assert result["status"] == 200
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_send_ai_host_request_fails_after_retry(self, repository):
        """Test _send_ai_host_request fails after retry."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            # Both calls return 401 - the method returns the response, doesn't raise
            mock_request.return_value = {
                "json": {"errorMessage": "Unauthorized"},
                "status": 401,
            }

            # The method returns the response after retries, doesn't raise RuntimeError
            result = await repository._send_ai_host_request(
                method="get", path="test/path"
            )

            assert result["status"] == 401
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_deployment_response_from_api_response_with_non_dict_data(self):
        """Test DeploymentResponse with non-dict data field."""
        api_response = {
            "success": True,
            "message": "Success",
            "data": "not a dict",
        }

        result = DeploymentResponse.from_api_response(api_response)

        assert result.success is True
        assert result.data is None

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_with_non_200_status(self, repository):
        """Test schedule_deploy_env with non-200 status."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {"message": "Accepted"},
                "status": 202,
            }

            with pytest.raises(Exception) as exc_info:
                await repository.schedule_deploy_env("env-tech-123")

            assert "Failed to schedule environment deployment" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_with_all_params(self, repository):
        """Test schedule_build_user_application with all parameters."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {
                    "success": True,
                    "message": "Build scheduled",
                    "build_id": "build-123",
                    "status": "pending",
                    "data": {"queue_position": 1},
                },
                "status": 200,
            }

            result = await repository.schedule_build_user_application(
                technical_id="app-tech-123",
                user_id="user-456",
                entity_data={"version": "2.0", "config": {"debug": True}},
            )

            assert result.success is True
            assert result.build_id == "build-123"
            assert result.status == "pending"
            assert result.data == {"queue_position": 1}

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_exception_handling(
        self, repository
    ):
        """Test schedule_deploy_user_application exception handling."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.side_effect = Exception("Network error")

            with pytest.raises(Exception) as exc_info:
                await repository.schedule_deploy_user_application("app-tech-123")

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_with_empty_response(self, repository):
        """Test get_env_deploy_status with empty response data."""
        with patch(
            "common.repository.cyoda.deployment_repository.send_request"
        ) as mock_request:
            mock_request.return_value = {
                "json": {},
                "status": 200,
            }

            result = await repository.get_env_deploy_status("build-123")

            assert isinstance(result, DeploymentResponse)
            assert result.success is False
            assert result.message == ""

    @pytest.mark.asyncio
    async def test_deployment_request_to_dict_with_none_entity(self):
        """Test DeploymentRequest.to_dict with None entity_data."""
        request = DeploymentRequest(
            technical_id="tech-123", user_id="user-1", entity_data=None, params=None
        )

        result = request.to_dict()

        assert result["technical_id"] == "tech-123"
        assert result["entity"] is None
        assert "params" not in result

    @pytest.mark.asyncio
    async def test_singleton_thread_safety(self, auth_service):
        """Test singleton thread safety."""
        import threading

        DeploymentRepository._instance = None
        instances = []

        def create_instance():
            instances.append(DeploymentRepository(auth_service))

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same
        assert all(inst is instances[0] for inst in instances)
