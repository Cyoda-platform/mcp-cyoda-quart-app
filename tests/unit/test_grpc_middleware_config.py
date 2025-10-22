"""
Unit tests for middleware configuration and builder system.
"""

from unittest.mock import Mock

import pytest

from common.grpc_client.middleware.base import MiddlewareLink
from common.grpc_client.middleware.config import (
    MiddlewareChainBuilder,
    MiddlewareChainConfig,
    MiddlewareConfig,
    MiddlewareRegistry,
    MiddlewareType,
    create_default_middleware_config,
    create_development_middleware_config,
    create_production_middleware_config,
    get_middleware_registry,
    register_custom_middleware,
)
from common.grpc_client.middleware.dispatch import DispatchMiddleware
from common.grpc_client.middleware.error import ErrorMiddleware
from common.grpc_client.middleware.logging import LoggingMiddleware
from common.grpc_client.middleware.metrics import MetricsMiddleware
from common.grpc_client.outbox import Outbox
from common.grpc_client.responses.builders import ResponseBuilderRegistry
from common.grpc_client.router import EventRouter


class TestMiddlewareConfig:
    """Test suite for MiddlewareConfig."""

    def test_middleware_config_creation(self):
        """Test creating middleware config."""
        config = MiddlewareConfig(type=MiddlewareType.LOGGING)

        assert config.type == MiddlewareType.LOGGING
        assert config.enabled is True
        assert config.config == {}
        assert config.priority == 100

    def test_middleware_config_with_custom_values(self):
        """Test creating middleware config with custom values."""
        config = MiddlewareConfig(
            type=MiddlewareType.METRICS,
            enabled=False,
            config={"verbose": True},
            priority=50,
        )

        assert config.type == MiddlewareType.METRICS
        assert config.enabled is False
        assert config.config == {"verbose": True}
        assert config.priority == 50


class TestMiddlewareChainConfig:
    """Test suite for MiddlewareChainConfig."""

    def test_chain_config_creation(self):
        """Test creating chain config."""
        config = MiddlewareChainConfig()

        assert config.middlewares == []

    def test_add_middleware(self):
        """Test adding middleware to chain config."""
        config = MiddlewareChainConfig()

        result = config.add_middleware(MiddlewareType.LOGGING)

        assert len(config.middlewares) == 1
        assert config.middlewares[0].type == MiddlewareType.LOGGING
        assert result is config  # Should return self for chaining

    def test_add_multiple_middlewares(self):
        """Test adding multiple middlewares."""
        config = MiddlewareChainConfig()

        config.add_middleware(MiddlewareType.LOGGING, priority=10)
        config.add_middleware(MiddlewareType.METRICS, priority=20)
        config.add_middleware(MiddlewareType.ERROR, priority=30)

        assert len(config.middlewares) == 3

    def test_add_middleware_with_config(self):
        """Test adding middleware with custom config."""
        config = MiddlewareChainConfig()

        config.add_middleware(
            MiddlewareType.LOGGING, enabled=False, config={"verbose": True}, priority=5
        )

        middleware = config.middlewares[0]
        assert middleware.enabled is False
        assert middleware.config == {"verbose": True}
        assert middleware.priority == 5

    def test_get_enabled_middlewares(self):
        """Test getting enabled middlewares."""
        config = MiddlewareChainConfig()

        config.add_middleware(MiddlewareType.LOGGING, enabled=True)
        config.add_middleware(MiddlewareType.METRICS, enabled=False)
        config.add_middleware(MiddlewareType.ERROR, enabled=True)

        enabled = config.get_enabled_middlewares()

        assert len(enabled) == 2
        assert all(m.enabled for m in enabled)

    def test_get_enabled_middlewares_sorted_by_priority(self):
        """Test that enabled middlewares are sorted by priority."""
        config = MiddlewareChainConfig()

        config.add_middleware(MiddlewareType.LOGGING, priority=30)
        config.add_middleware(MiddlewareType.METRICS, priority=10)
        config.add_middleware(MiddlewareType.ERROR, priority=20)

        enabled = config.get_enabled_middlewares()

        assert enabled[0].type == MiddlewareType.METRICS  # priority 10
        assert enabled[1].type == MiddlewareType.ERROR  # priority 20
        assert enabled[2].type == MiddlewareType.LOGGING  # priority 30

    def test_chaining_add_middleware(self):
        """Test chaining add_middleware calls."""
        config = MiddlewareChainConfig()

        config.add_middleware(MiddlewareType.LOGGING).add_middleware(
            MiddlewareType.METRICS
        ).add_middleware(MiddlewareType.ERROR)

        assert len(config.middlewares) == 3


class TestMiddlewareRegistry:
    """Test suite for MiddlewareRegistry."""

    @pytest.fixture
    def registry(self):
        """Create MiddlewareRegistry instance."""
        return MiddlewareRegistry()

    def test_registry_initialization(self, registry):
        """Test registry initializes with default middlewares."""
        # Should have default middlewares registered
        assert MiddlewareType.LOGGING in registry._factories
        assert MiddlewareType.METRICS in registry._factories
        assert MiddlewareType.ERROR in registry._factories
        assert MiddlewareType.DISPATCH in registry._factories

    def test_create_logging_middleware(self, registry):
        """Test creating logging middleware."""
        config = MiddlewareConfig(type=MiddlewareType.LOGGING)

        middleware = registry.create_middleware(config)

        assert isinstance(middleware, LoggingMiddleware)

    def test_create_metrics_middleware(self, registry):
        """Test creating metrics middleware."""
        config = MiddlewareConfig(type=MiddlewareType.METRICS)

        middleware = registry.create_middleware(config)

        assert isinstance(middleware, MetricsMiddleware)

    def test_create_error_middleware(self, registry):
        """Test creating error middleware."""
        config = MiddlewareConfig(type=MiddlewareType.ERROR)

        middleware = registry.create_middleware(config)

        assert isinstance(middleware, ErrorMiddleware)

    def test_create_dispatch_middleware(self, registry):
        """Test creating dispatch middleware."""
        config = MiddlewareConfig(type=MiddlewareType.DISPATCH)
        router = EventRouter()
        builders = ResponseBuilderRegistry()
        outbox = Outbox()

        middleware = registry.create_middleware(
            config, router=router, builders=builders, outbox=outbox
        )

        assert isinstance(middleware, DispatchMiddleware)

    def test_create_dispatch_middleware_missing_dependencies(self, registry):
        """Test creating dispatch middleware without required dependencies."""
        config = MiddlewareConfig(type=MiddlewareType.DISPATCH)

        with pytest.raises(ValueError) as exc_info:
            registry.create_middleware(config)

        assert "requires router, builders, and outbox" in str(exc_info.value)

    def test_register_custom_middleware(self, registry):
        """Test registering custom middleware."""

        def custom_factory(config, **kwargs):
            return MiddlewareLink()

        registry.register_middleware(MiddlewareType.CUSTOM, custom_factory)

        assert MiddlewareType.CUSTOM in registry._factories

    def test_create_custom_middleware(self, registry):
        """Test creating custom middleware."""

        class CustomMiddleware(MiddlewareLink):
            pass

        def custom_factory(config, **kwargs):
            return CustomMiddleware()

        registry.register_middleware(MiddlewareType.CUSTOM, custom_factory)
        config = MiddlewareConfig(type=MiddlewareType.CUSTOM)

        middleware = registry.create_middleware(config)

        assert isinstance(middleware, CustomMiddleware)

    def test_create_unknown_middleware_raises_error(self, registry):
        """Test creating unknown middleware type raises error."""
        # Create a config with a type not in the registry
        config = Mock()
        config.type = "UnknownType"

        with pytest.raises(ValueError) as exc_info:
            registry.create_middleware(config)

        assert "Unknown middleware type" in str(exc_info.value)


class TestMiddlewareChainBuilder:
    """Test suite for MiddlewareChainBuilder."""

    @pytest.fixture
    def builder(self):
        """Create MiddlewareChainBuilder instance."""
        return MiddlewareChainBuilder()

    @pytest.fixture
    def dispatch_kwargs(self):
        """Create kwargs for dispatch middleware."""
        return {
            "router": EventRouter(),
            "builders": ResponseBuilderRegistry(),
            "outbox": Outbox(),
        }

    def test_builder_initialization(self, builder):
        """Test builder initialization."""
        assert builder.registry is not None
        assert isinstance(builder.registry, MiddlewareRegistry)

    def test_builder_with_custom_registry(self):
        """Test builder with custom registry."""
        custom_registry = MiddlewareRegistry()
        builder = MiddlewareChainBuilder(registry=custom_registry)

        assert builder.registry is custom_registry

    def test_build_chain_with_single_middleware(self, builder, dispatch_kwargs):
        """Test building chain with single middleware."""
        config = MiddlewareChainConfig()
        config.add_middleware(MiddlewareType.LOGGING)

        first_middleware = builder.build_chain(config)

        assert first_middleware is not None
        assert isinstance(first_middleware, LoggingMiddleware)

    def test_build_chain_with_multiple_middlewares(self, builder, dispatch_kwargs):
        """Test building chain with multiple middlewares."""
        config = MiddlewareChainConfig()
        config.add_middleware(MiddlewareType.LOGGING, priority=10)
        config.add_middleware(MiddlewareType.ERROR, priority=20)

        first_middleware = builder.build_chain(config)

        assert first_middleware is not None
        assert isinstance(first_middleware, LoggingMiddleware)
        # Second middleware should be chained
        assert first_middleware._successor is not None
        assert isinstance(first_middleware._successor, ErrorMiddleware)

    def test_build_chain_respects_priority(self, builder, dispatch_kwargs):
        """Test that chain building respects priority order."""
        config = MiddlewareChainConfig()
        config.add_middleware(MiddlewareType.ERROR, priority=30)
        config.add_middleware(MiddlewareType.LOGGING, priority=10)
        config.add_middleware(MiddlewareType.METRICS, priority=20)

        first_middleware = builder.build_chain(config)

        # Should be in priority order: LOGGING (10), METRICS (20), ERROR (30)
        assert isinstance(first_middleware, LoggingMiddleware)
        assert isinstance(first_middleware._successor, MetricsMiddleware)
        assert isinstance(first_middleware._successor._successor, ErrorMiddleware)

    def test_build_chain_with_no_enabled_middlewares(self, builder):
        """Test building chain with no enabled middlewares."""
        config = MiddlewareChainConfig()
        config.add_middleware(MiddlewareType.LOGGING, enabled=False)

        result = builder.build_chain(config)

        assert result is None

    def test_build_chain_with_empty_config(self, builder):
        """Test building chain with empty config."""
        config = MiddlewareChainConfig()

        result = builder.build_chain(config)

        assert result is None

    def test_build_chain_with_dispatch_middleware(self, builder, dispatch_kwargs):
        """Test building chain including dispatch middleware."""
        config = MiddlewareChainConfig()
        config.add_middleware(MiddlewareType.LOGGING, priority=10)
        config.add_middleware(MiddlewareType.DISPATCH, priority=20)

        first_middleware = builder.build_chain(config, **dispatch_kwargs)

        assert first_middleware is not None
        assert isinstance(first_middleware, LoggingMiddleware)
        assert isinstance(first_middleware._successor, DispatchMiddleware)


class TestConfigurationFunctions:
    """Test suite for configuration helper functions."""

    def test_create_default_middleware_config(self):
        """Test creating default middleware config."""
        config = create_default_middleware_config()

        assert len(config.middlewares) == 4
        # Verify all default middlewares are present
        types = [m.type for m in config.middlewares]
        assert MiddlewareType.LOGGING in types
        assert MiddlewareType.METRICS in types
        assert MiddlewareType.ERROR in types
        assert MiddlewareType.DISPATCH in types

    def test_default_config_priority_order(self):
        """Test that default config has correct priority order."""
        config = create_default_middleware_config()
        enabled = config.get_enabled_middlewares()

        # Should be in priority order
        assert enabled[0].type == MiddlewareType.LOGGING  # priority 10
        assert enabled[1].type == MiddlewareType.METRICS  # priority 20
        assert enabled[2].type == MiddlewareType.ERROR  # priority 30
        assert enabled[3].type == MiddlewareType.DISPATCH  # priority 40

    def test_create_development_middleware_config(self):
        """Test creating development middleware config."""
        config = create_development_middleware_config()

        # Should have verbose logging enabled
        logging_middleware = next(
            m for m in config.middlewares if m.type == MiddlewareType.LOGGING
        )
        assert logging_middleware.config.get("verbose") is True

    def test_create_production_middleware_config(self):
        """Test creating production middleware config."""
        config = create_production_middleware_config()

        # Should have detailed metrics enabled
        metrics_middleware = next(
            m for m in config.middlewares if m.type == MiddlewareType.METRICS
        )
        assert metrics_middleware.config.get("detailed_metrics") is True

    def test_get_middleware_registry(self):
        """Test getting global middleware registry."""
        registry = get_middleware_registry()

        assert isinstance(registry, MiddlewareRegistry)

    def test_register_custom_middleware_global(self):
        """Test registering custom middleware with global registry."""

        def custom_factory(config, **kwargs):
            return MiddlewareLink()

        register_custom_middleware(MiddlewareType.CUSTOM, custom_factory)

        registry = get_middleware_registry()
        assert MiddlewareType.CUSTOM in registry._factories

