"""
Dependency injection container using dependency-injector library.

This module provides a centralized container for all application services
using the well-established dependency-injector framework.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from common.interfaces.services import (
    IAuthService, IRepository, IEntityService, IProcessorManager, IGrpcClient
)

logger = logging.getLogger(__name__)


def _create_auth_service(client_id: str, client_secret: str, token_url: str, scope: str = "read write"):
    """Create auth service with lazy import."""
    from common.auth.cyoda_auth import CyodaAuthService
    return CyodaAuthService(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        scope=scope
    )


def _create_repository(auth_service, use_in_memory: bool):
    """Create repository with lazy import."""
    if use_in_memory:
        from common.repository.in_memory_db import InMemoryRepository
        return InMemoryRepository()
    else:
        from common.repository.cyoda.cyoda_repository import CyodaRepository
        return CyodaRepository(cyoda_auth_service=auth_service)


def _create_entity_service(repository):
    """Create entity service with lazy import."""
    from common.service.service import EntityServiceImpl
    return EntityServiceImpl(repository=repository)


def _create_grpc_client(auth_service):
    """Create gRPC client with lazy import."""
    from common.grpc_client.grpc_client import GrpcClient
    return GrpcClient(auth=auth_service)


def _create_processor_manager(modules):
    """Create processor manager with lazy import."""
    from common.processor import get_processor_manager
    return get_processor_manager(modules)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Application dependency injection container.

    This container defines all the services and their dependencies using
    the dependency-injector framework with lazy imports to avoid configuration issues.
    """

    # Configuration
    config = providers.Configuration()

    # Core services
    auth_service = providers.Singleton(
        _create_auth_service,
        client_id=config.authentication.client_id,
        client_secret=config.authentication.client_secret,
        token_url=config.authentication.token_url,
        scope=config.authentication.scope,
    )

    # Repository - can be either Cyoda or InMemory based on config
    repository = providers.Singleton(
        _create_repository,
        auth_service=auth_service,
        use_in_memory=config.repository.use_in_memory.as_(bool),
    )

    # Entity service
    entity_service = providers.Singleton(
        _create_entity_service,
        repository=repository,
    )

    # Processor manager
    processor_manager = providers.Singleton(
        _create_processor_manager,
        modules=config.processor.modules.as_(list),
    )

    # gRPC client
    grpc_client = providers.Singleton(
        _create_grpc_client,
        auth_service=auth_service,
    )

    # Utilities
    chat_lock = providers.Singleton(asyncio.Lock)


class ServiceContainer:
    """
    Service container wrapper that provides a clean interface to the DI container.
    
    This class wraps the dependency-injector container and provides methods
    for service access and configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the service container.
        
        Args:
            config: Configuration dictionary for the container.
        """
        self.container = ApplicationContainer()
        self._initialized = False
        
        if config:
            self.configure(config)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the container with the provided configuration.
        
        Args:
            config: Configuration dictionary.
        """
        # Set default configuration values
        default_config = {
            'authentication': {
                'client_id': '',
                'client_secret': '',
                'token_url': '',
                'scope': 'read write',
            },
            'repository': {
                'use_in_memory': True,  # Default to in-memory for testing
            },
            'processor': {
                'modules': ['workflow.processors', 'workflow.criteria'],
            },
        }
        
        # Merge with provided config
        merged_config = self._deep_merge(default_config, config)
        
        # Configure the container
        self.container.config.from_dict(merged_config)
        
        logger.info("Service container configured successfully")
    
    def initialize(self) -> None:
        """Initialize the container and wire dependencies."""
        if self._initialized:
            logger.warning("Service container already initialized")
            return

        # Skip wiring for now to avoid configuration issues
        # The container can still be used without wiring
        # self.container.wire(modules=[
        #     'common.grpc_client.handlers.calc',
        #     'common.grpc_client.handlers.criteria_calc',
        #     'common.grpc_client.factory',
        #     'service.registry',
        # ])

        self._initialized = True
        logger.info("Service container initialized successfully")
    
    def get_service(self, service_type: type) -> Any:
        """
        Get a service by type.
        
        Args:
            service_type: Type of the service to retrieve.
            
        Returns:
            The requested service instance.
        """
        if not self._initialized:
            raise RuntimeError("Service container not initialized. Call initialize() first.")
        
        # Map service types to container providers
        service_mapping = {
            IAuthService: self.container.auth_service,
            IRepository: self.container.repository,
            IEntityService: self.container.entity_service,
            IProcessorManager: self.container.processor_manager,
            IGrpcClient: self.container.grpc_client,
            asyncio.Lock: self.container.chat_lock,
        }
        
        if service_type not in service_mapping:
            raise ValueError(f"Service type '{service_type.__name__}' not registered")
        
        return service_mapping[service_type]()
    

    
    def is_initialized(self) -> bool:
        """
        Check if the container is initialized.
        
        Returns:
            True if initialized, False otherwise.
        """
        return self._initialized
    
    def shutdown(self) -> None:
        """Shutdown the container and clean up resources."""
        if self._initialized:
            self.container.unwire()
            self._initialized = False
            logger.info("Service container shut down successfully")
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary.
            override: Dictionary to merge into base.
            
        Returns:
            Merged dictionary.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ServiceContainer._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """
    Get the global service container instance.
    
    Returns:
        The global ServiceContainer instance.
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def initialize_container(config: Optional[Dict[str, Any]] = None) -> ServiceContainer:
    """
    Initialize the global service container.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        The initialized ServiceContainer instance.
    """
    container = get_container()
    if config:
        container.configure(config)
    container.initialize()
    return container
