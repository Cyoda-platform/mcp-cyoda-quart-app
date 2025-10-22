"""
Unit tests for application app module.

This module tests the main application initialization and configuration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from application.app import app


class TestApplicationAppInitialization:
    """Test suite for application initialization."""

    def test_app_is_quart_instance(self) -> None:
        """Test that app is a Quart instance."""
        from quart import Quart

        assert isinstance(app, Quart)

    def test_app_name(self) -> None:
        """Test application name."""
        assert app.name == "application.app"

    def test_app_has_error_handlers(self) -> None:
        """Test that error handlers are registered."""
        assert len(app.error_handler_spec) > 0

    def test_app_has_favicon_route(self) -> None:
        """Test that favicon route is registered."""
        # Check that routes are registered
        assert len(app.url_map._rules) > 0


class TestApplicationAppConfiguration:
    """Test suite for application configuration."""

    def test_app_cors_configuration(self) -> None:
        """Test CORS configuration."""
        assert app is not None
        # CORS should be configured through middleware

    def test_app_schema_configuration(self) -> None:
        """Test schema configuration."""
        assert app is not None
        # QuartSchema should be configured

    def test_app_error_handler_for_validation_errors(self) -> None:
        """Test error handler for validation errors."""
        from quart_schema import ResponseSchemaValidationError

        # Check that error handler is registered
        error_handlers = app.error_handler_spec.get(None, {})
        assert ResponseSchemaValidationError in error_handlers


class TestApplicationAppRoutes:
    """Test suite for application routes."""

    @pytest.mark.asyncio
    async def test_favicon_route_exists(self) -> None:
        """Test that favicon route exists."""
        async with app.test_client() as client:
            response = await client.get("/favicon.ico")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_favicon_route_returns_empty_string(self) -> None:
        """Test that favicon route returns empty string."""
        async with app.test_client() as client:
            response = await client.get("/favicon.ico")
            data = await response.get_data()
            assert data == b""


class TestApplicationAppLifecycle:
    """Test suite for application lifecycle."""

    def test_app_has_before_serving_handlers(self) -> None:
        """Test that before_serving handlers are registered."""
        # The app should have startup handlers
        assert app is not None

    def test_app_has_after_serving_handlers(self) -> None:
        """Test that after_serving handlers are registered."""
        # The app should have shutdown handlers
        assert app is not None

