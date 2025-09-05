"""
Service interfaces for dependency injection and loose coupling.

This module defines abstract interfaces for all major services in the system,
enabling proper dependency inversion and testability.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from entity.cyoda_entity import CyodaEntity

# Generic type for repository entities
T = TypeVar('T')


class IAuthService(ABC):
    """Interface for authentication services."""
    
    @abstractmethod
    def get_access_token_sync(self) -> str:
        """Get access token synchronously."""
        pass
    
    @abstractmethod
    async def get_access_token(self) -> str:
        """Get access token asynchronously."""
        pass
    
    @abstractmethod
    def invalidate_token(self) -> None:
        """Invalidate current token."""
        pass


class IGrpcClient(ABC):
    """Interface for gRPC client."""
    
    @abstractmethod
    async def grpc_stream(self) -> None:
        """Start the gRPC streaming connection."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the gRPC client."""
        pass


class IEventRouter(ABC):
    """Interface for event routing."""
    
    @abstractmethod
    def register(self, event_type: str, handler: Any) -> None:
        """Register an event handler."""
        pass
    
    @abstractmethod
    def route(self, event: Any) -> Optional[Any]:
        """Route an event to its handler."""
        pass


class IResponseBuilder(ABC):
    """Interface for response builders."""
    
    @abstractmethod
    def build(self, data: Dict[str, Any]) -> Any:
        """Build a response from data."""
        pass


class IMiddleware(ABC):
    """Interface for middleware components."""
    
    @abstractmethod
    async def handle(self, event: Any) -> Any:
        """Handle an event."""
        pass
    
    @abstractmethod
    def set_successor(self, successor: 'IMiddleware') -> 'IMiddleware':
        """Set the next middleware in the chain."""
        pass


class IConfigurationProvider(ABC):
    """Interface for configuration providers."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a configuration section."""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if a configuration key exists."""
        pass


class ILogger(Protocol):
    """Protocol for logger interface."""
    
    def debug(self, message: str, *args, **kwargs) -> None: ...
    def info(self, message: str, *args, **kwargs) -> None: ...
    def warning(self, message: str, *args, **kwargs) -> None: ...
    def error(self, message: str, *args, **kwargs) -> None: ...
    def exception(self, message: str, *args, **kwargs) -> None: ...


class IMetricsCollector(ABC):
    """Interface for metrics collection."""
    
    @abstractmethod
    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        pass
    
    @abstractmethod
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        pass
    
    @abstractmethod
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        pass
    
    @abstractmethod
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> Any:
        """Start a timer for measuring duration."""
        pass


class IHealthChecker(ABC):
    """Interface for health checking."""
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check the health of the service."""
        pass
    
    @abstractmethod
    def register_health_check(self, name: str, check_func: Any) -> None:
        """Register a health check function."""
        pass


class IEventPublisher(ABC):
    """Interface for event publishing."""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event."""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type."""
        pass


class IServiceRegistry(ABC):
    """Interface for service registry."""

    @abstractmethod
    def register_service(self, name: str, service: Any) -> None:
        """Register a service."""
        pass

    @abstractmethod
    def get_service(self, name: str) -> Any:
        """Get a service by name."""
        pass

    @abstractmethod
    def has_service(self, name: str) -> bool:
        """Check if a service is registered."""
        pass

    @abstractmethod
    def list_services(self) -> List[str]:
        """List all registered services."""
        pass


class IProcessorManager(ABC):
    """Interface for processor manager."""

    @abstractmethod
    def register_processor(self, processor: Any) -> None:
        """Register a processor instance."""
        pass

    @abstractmethod
    def register_criteria(self, criteria: Any) -> None:
        """Register a criteria checker instance."""
        pass

    @abstractmethod
    async def process_entity(self, processor_name: str, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process an entity using the specified processor."""
        pass

    @abstractmethod
    async def check_criteria(self, criteria_name: str, entity: CyodaEntity, **kwargs) -> bool:
        """Check if entity meets the specified criteria."""
        pass

    @abstractmethod
    def list_processors(self) -> List[str]:
        """List available processors."""
        pass

    @abstractmethod
    def list_criteria(self) -> List[str]:
        """List available criteria."""
        pass

    @abstractmethod
    def get_processor_info(self, processor_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a processor."""
        pass

    @abstractmethod
    def get_criteria_info(self, criteria_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a criteria checker."""
        pass


# Type aliases for commonly used interfaces
AuthService = IAuthService
GrpcClient = IGrpcClient
EventRouter = IEventRouter
ResponseBuilder = IResponseBuilder
Middleware = IMiddleware
ConfigurationProvider = IConfigurationProvider
MetricsCollector = IMetricsCollector
HealthChecker = IHealthChecker
EventPublisher = IEventPublisher
ServiceRegistry = IServiceRegistry
ProcessorManager = IProcessorManager
