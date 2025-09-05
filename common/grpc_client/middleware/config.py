"""
Middleware configuration and builder system.

This module provides a flexible way to configure and build middleware chains
with proper separation of concerns and extensibility.
"""

import logging
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass, field
from enum import Enum

from .base import MiddlewareLink
from .logging import LoggingMiddleware
from .metrics import MetricsMiddleware
from .error import ErrorMiddleware
from .dispatch import DispatchMiddleware

logger = logging.getLogger(__name__)


class MiddlewareType(Enum):
    """Types of middleware available in the system."""
    LOGGING = "logging"
    METRICS = "metrics"
    ERROR = "error"
    DISPATCH = "dispatch"
    CUSTOM = "custom"


@dataclass
class MiddlewareConfig:
    """Configuration for a single middleware."""
    type: MiddlewareType
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100  # Lower numbers execute first


@dataclass
class MiddlewareChainConfig:
    """Configuration for the entire middleware chain."""
    middlewares: List[MiddlewareConfig] = field(default_factory=list)
    
    def add_middleware(
        self,
        middleware_type: MiddlewareType,
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None,
        priority: int = 100
    ) -> 'MiddlewareChainConfig':
        """Add a middleware to the chain configuration."""
        self.middlewares.append(MiddlewareConfig(
            type=middleware_type,
            enabled=enabled,
            config=config or {},
            priority=priority
        ))
        return self
    
    def get_enabled_middlewares(self) -> List[MiddlewareConfig]:
        """Get all enabled middlewares sorted by priority."""
        enabled = [m for m in self.middlewares if m.enabled]
        return sorted(enabled, key=lambda x: x.priority)


class MiddlewareRegistry:
    """Registry for middleware types and their factory functions."""
    
    def __init__(self):
        self._factories: Dict[MiddlewareType, callable] = {}
        self._register_default_middlewares()
    
    def _register_default_middlewares(self):
        """Register default middleware factories."""
        self._factories[MiddlewareType.LOGGING] = self._create_logging_middleware
        self._factories[MiddlewareType.METRICS] = self._create_metrics_middleware
        self._factories[MiddlewareType.ERROR] = self._create_error_middleware
        self._factories[MiddlewareType.DISPATCH] = self._create_dispatch_middleware
    
    def register_middleware(
        self,
        middleware_type: MiddlewareType,
        factory: callable
    ):
        """Register a custom middleware factory."""
        self._factories[middleware_type] = factory
        logger.info(f"Registered middleware factory for type: {middleware_type}")
    
    def create_middleware(
        self,
        config: MiddlewareConfig,
        **kwargs
    ) -> MiddlewareLink:
        """Create a middleware instance from configuration."""
        if config.type not in self._factories:
            raise ValueError(f"Unknown middleware type: {config.type}")
        
        factory = self._factories[config.type]
        try:
            return factory(config.config, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create middleware {config.type}: {e}")
            raise
    
    def _create_logging_middleware(self, config: Dict[str, Any], **kwargs) -> LoggingMiddleware:
        """Create logging middleware with configuration."""
        return LoggingMiddleware()
    
    def _create_metrics_middleware(self, config: Dict[str, Any], **kwargs) -> MetricsMiddleware:
        """Create metrics middleware with configuration."""
        return MetricsMiddleware()
    
    def _create_error_middleware(self, config: Dict[str, Any], **kwargs) -> ErrorMiddleware:
        """Create error middleware with configuration."""
        return ErrorMiddleware()
    
    def _create_dispatch_middleware(self, config: Dict[str, Any], **kwargs) -> DispatchMiddleware:
        """Create dispatch middleware with configuration."""
        # Extract required dependencies from kwargs
        router = kwargs.get('router')
        builders = kwargs.get('builders')
        outbox = kwargs.get('outbox')
        services = kwargs.get('services')
        
        if not all([router, builders, outbox]):
            raise ValueError("DispatchMiddleware requires router, builders, and outbox")
        
        return DispatchMiddleware(
            router=router,
            builders=builders,
            outbox=outbox,
            services=services
        )


class MiddlewareChainBuilder:
    """Builder for creating configured middleware chains."""
    
    def __init__(self, registry: Optional[MiddlewareRegistry] = None):
        self.registry = registry or MiddlewareRegistry()
    
    def build_chain(
        self,
        config: MiddlewareChainConfig,
        **kwargs
    ) -> Optional[MiddlewareLink]:
        """
        Build a middleware chain from configuration.
        
        Args:
            config: The middleware chain configuration
            **kwargs: Additional arguments passed to middleware factories
            
        Returns:
            The first middleware in the chain, or None if no middlewares
        """
        enabled_middlewares = config.get_enabled_middlewares()
        
        if not enabled_middlewares:
            logger.warning("No enabled middlewares found in configuration")
            return None
        
        # Create middleware instances
        middleware_instances = []
        for middleware_config in enabled_middlewares:
            try:
                middleware = self.registry.create_middleware(middleware_config, **kwargs)
                middleware_instances.append(middleware)
                logger.debug(f"Created middleware: {middleware_config.type}")
            except Exception as e:
                logger.error(f"Failed to create middleware {middleware_config.type}: {e}")
                # Continue with other middlewares
                continue
        
        if not middleware_instances:
            logger.error("No middleware instances could be created")
            return None
        
        # Chain middlewares together
        for i in range(len(middleware_instances) - 1):
            middleware_instances[i].set_successor(middleware_instances[i + 1])
        
        logger.info(f"Built middleware chain with {len(middleware_instances)} middlewares")
        return middleware_instances[0]


def create_default_middleware_config() -> MiddlewareChainConfig:
    """Create the default middleware chain configuration."""
    config = MiddlewareChainConfig()
    
    # Add middlewares in order of execution
    config.add_middleware(MiddlewareType.LOGGING, priority=10)
    config.add_middleware(MiddlewareType.METRICS, priority=20)
    config.add_middleware(MiddlewareType.ERROR, priority=30)
    config.add_middleware(MiddlewareType.DISPATCH, priority=40)
    
    return config


def create_development_middleware_config() -> MiddlewareChainConfig:
    """Create middleware configuration optimized for development."""
    config = create_default_middleware_config()
    
    # Enable more verbose logging in development
    for middleware in config.middlewares:
        if middleware.type == MiddlewareType.LOGGING:
            middleware.config["verbose"] = True
    
    return config


def create_production_middleware_config() -> MiddlewareChainConfig:
    """Create middleware configuration optimized for production."""
    config = create_default_middleware_config()
    
    # Enable metrics in production
    for middleware in config.middlewares:
        if middleware.type == MiddlewareType.METRICS:
            middleware.config["detailed_metrics"] = True
    
    return config


# Global registry instance
_registry = MiddlewareRegistry()


def get_middleware_registry() -> MiddlewareRegistry:
    """Get the global middleware registry."""
    return _registry


def register_custom_middleware(middleware_type: MiddlewareType, factory: callable):
    """Register a custom middleware with the global registry."""
    _registry.register_middleware(middleware_type, factory)
