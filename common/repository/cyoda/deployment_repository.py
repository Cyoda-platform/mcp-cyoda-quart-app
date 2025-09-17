"""
Deployment Repository Implementation

Repository for interacting with AI Host Deployment API endpoints.
Provides operations for scheduling and managing deployments.
"""

import json
import logging
import threading
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Protocol

from common.config.config import CYODA_AI_URL
from common.utils.utils import custom_serializer, send_request

logger = logging.getLogger(__name__)


class AuthService(Protocol):
    """Minimal protocol for the auth service this repo depends on."""

    async def get_access_token(self) -> str: ...

    def invalidate_tokens(self) -> None: ...


@dataclass
class DeploymentRequest:
    """Base deployment request structure."""

    technical_id: str
    user_id: Optional[str] = None
    entity_data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        result: Dict[str, Any] = {
            "technical_id": self.technical_id,
            "entity": self.entity_data,
        }
        if self.params:
            result["params"] = self.params
        return result


@dataclass
class DeploymentResponse:
    """Response from deployment operations."""

    success: bool
    message: str
    build_id: Optional[str] = None
    status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> "DeploymentResponse":
        """Create DeploymentResponse from API response data."""
        return cls(
            success=bool(response_data.get("success", False)),
            message=str(response_data.get("message", "")),
            build_id=response_data.get("build_id"),
            status=response_data.get("status"),
            data=(
                response_data.get("data", {})
                if isinstance(response_data.get("data", {}), dict)
                else None
            ),
        )


class DeploymentRepository:
    """
    Repository for deployment operations using AI Host API.
    Thread-safe singleton implementation.
    """

    _instance: ClassVar[Optional["DeploymentRepository"]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    # Instance attributes (initialized in __new__/__init__)
    _cyoda_auth_service: AuthService
    _initialized: bool

    def __new__(cls, cyoda_auth_service: AuthService) -> "DeploymentRepository":
        """Thread-safe singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                # Stash dependencies/flags on first construction
                instance._cyoda_auth_service = cyoda_auth_service
                instance._initialized = False
                cls._instance = instance
        # If already created, we still return the same instance
        return cls._instance  # type: ignore[return-value]

    def __init__(self, cyoda_auth_service: AuthService) -> None:
        """Initialize the repository."""
        # Only initialize once for the singleton
        if not getattr(self, "_initialized", False):
            self._cyoda_auth_service = cyoda_auth_service
            self._initialized = True
            logger.info("DeploymentRepository initialized")

    async def _send_ai_host_request(
        self,
        method: str,
        path: str,
        data: Optional[str] = None,
        base_url: str = CYODA_AI_URL,
    ) -> Dict[str, Any]:
        """
        Send an HTTP request to the AI Host API with automatic retry on 401.
        """
        token: str = await self._cyoda_auth_service.get_access_token()

        for attempt in range(2):
            try:
                # Prepare headers
                headers: Dict[str, str] = {
                    "Content-Type": "application/json",
                    "Authorization": (
                        f"Bearer {token}" if not token.startswith("Bearer") else token
                    ),
                }

                url = f"{base_url}/{path}"

                # Send request
                response: Dict[str, Any] = await send_request(
                    headers, url, method, data=data
                )

            except Exception as exc:
                msg = str(exc)
                if attempt == 0 and ("401" in msg or "Unauthorized" in msg):
                    logger.warning(
                        f"Request to {path} failed with 401; invalidating tokens and retrying"
                    )
                    self._cyoda_auth_service.invalidate_tokens()
                    token = await self._cyoda_auth_service.get_access_token()
                    continue
                raise

            status = response.get("status") if isinstance(response, dict) else None
            if attempt == 0 and status == 401:
                logger.warning(
                    f"Response from {path} returned status 401; invalidating tokens and retrying"
                )
                self._cyoda_auth_service.invalidate_tokens()
                token = await self._cyoda_auth_service.get_access_token()
                continue

            return response

        raise RuntimeError(f"Failed request {method.upper()} {path} after retry")

    async def schedule_deploy_env(self, technical_id: str) -> DeploymentResponse:
        """
        Schedule environment deployment.

        Args:
            technical_id: Technical ID of the environment

        Returns:
            DeploymentResponse object

        Raises:
            Exception: If the API request fails
        """
        try:
            path = "deployment/schedule/env"

            request_obj = DeploymentRequest(technical_id=technical_id)

            data = json.dumps(request_obj.to_dict(), default=custom_serializer)

            logger.info(f"Scheduling environment deployment for {technical_id}")

            response = await self._send_ai_host_request(
                method="post", path=path, data=data
            )

            if response.get("status") != 200:
                logger.error(f"Failed to schedule environment deployment: {response}")
                raise Exception(
                    f"Failed to schedule environment deployment: {response.get('json')}"
                )

            response_data = response.get("json", {})
            deployment_response = DeploymentResponse.from_api_response(
                response_data if isinstance(response_data, dict) else {}
            )

            logger.info(
                f"Successfully scheduled environment deployment for {technical_id}"
            )
            return deployment_response

        except Exception as e:
            logger.exception(
                f"Error scheduling environment deployment for {technical_id}: {e}"
            )
            raise

    async def schedule_build_user_application(
        self,
        technical_id: str,
        user_id: Optional[str] = None,
        entity_data: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResponse:
        """
        Schedule user application build.

        Args:
            technical_id: Technical ID of the application
            user_id: User ID initiating the build
            entity_data: Entity data for build

        Returns:
            DeploymentResponse object

        Raises:
            Exception: If the API request fails
        """
        try:
            path = "deployment/schedule/user-app/build"

            request_obj = DeploymentRequest(
                technical_id=technical_id, user_id=user_id, entity_data=entity_data
            )

            data = json.dumps(request_obj.to_dict(), default=custom_serializer)

            logger.info(f"Scheduling user application build for {technical_id}")

            response = await self._send_ai_host_request(
                method="post", path=path, data=data
            )

            if response.get("status") != 200:
                logger.error(f"Failed to schedule user application build: {response}")
                raise Exception(
                    f"Failed to schedule user application build: {response.get('json')}"
                )

            response_data = response.get("json", {})
            deployment_response = DeploymentResponse.from_api_response(
                response_data if isinstance(response_data, dict) else {}
            )

            logger.info(
                f"Successfully scheduled user application build for {technical_id}"
            )
            return deployment_response

        except Exception as e:
            logger.exception(
                f"Error scheduling user application build for {technical_id}: {e}"
            )
            raise

    async def schedule_deploy_user_application(
        self,
        technical_id: str,
        user_id: Optional[str] = None,
        entity_data: Optional[Dict[str, Any]] = None,
    ) -> DeploymentResponse:
        """
        Schedule user application deployment.

        Args:
            technical_id: Technical ID of the application
            user_id: User ID initiating the deployment
            entity_data: Entity data for deployment

        Returns:
            DeploymentResponse object

        Raises:
            Exception: If the API request fails
        """
        try:
            path = "deployment/schedule/user-app/deploy"

            request_obj = DeploymentRequest(
                technical_id=technical_id, user_id=user_id, entity_data=entity_data
            )

            data = json.dumps(request_obj.to_dict(), default=custom_serializer)

            logger.info(f"Scheduling user application deployment for {technical_id}")

            response = await self._send_ai_host_request(
                method="post", path=path, data=data
            )

            if response.get("status") != 200:
                logger.error(
                    f"Failed to schedule user application deployment: {response}"
                )
                raise Exception(
                    f"Failed to schedule user application deployment: {response.get('json')}"
                )

            response_data = response.get("json", {})
            deployment_response = DeploymentResponse.from_api_response(
                response_data if isinstance(response_data, dict) else {}
            )

            logger.info(
                f"Successfully scheduled user application deployment for {technical_id}"
            )
            return deployment_response

        except Exception as e:
            logger.exception(
                f"Error scheduling user application deployment for {technical_id}: {e}"
            )
            raise

    async def get_env_deploy_status(
        self, build_id: str, user_id: Optional[str] = None
    ) -> DeploymentResponse:
        """
        Get deployment status for a specific build.

        Args:
            build_id: Build ID to check status for
            user_id: Optional user ID (currently unused)

        Returns:
            DeploymentResponse object

        Raises:
            Exception: If the API request fails
        """
        try:
            path = f"deployment/status/{build_id}"

            logger.info(f"Getting deployment status for build {build_id}")

            response = await self._send_ai_host_request(method="get", path=path)

            if response.get("status") != 200:
                logger.error(f"Failed to get deployment status: {response}")
                raise Exception(
                    f"Failed to get deployment status: {response.get('json')}"
                )

            response_data = response.get("json", {})
            deployment_response = DeploymentResponse.from_api_response(
                response_data if isinstance(response_data, dict) else {}
            )

            logger.info(
                f"Successfully retrieved deployment status for build {build_id}"
            )
            return deployment_response

        except Exception as e:
            logger.exception(
                f"Error getting deployment status for build {build_id}: {e}"
            )
            raise
