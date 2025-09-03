"""
Modern Service Registry using dependency-injector.

This module provides a clean registry pattern for accessing services
throughout the application using dependency-injector.
"""

import logging
from typing import Any, Optional, Dict

from .factory import ServiceFactory
from .container import get_container
from common.interfaces.services import (
    IAuthService, IRepository, IEntityService, IProcessorManager, IGrpcClient
)

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Modern service registry using dependency-injector container.
    
    This registry provides a clean interface for accessing services
    throughout the application.
    """
    
    _instance: Optional['ServiceRegistry'] = None
    _factory: Optional[ServiceFactory] = None
    
    def __new__(cls) -> 'ServiceRegistry':
        """Ensure only one instance of the registry exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the service registry with a service factory.
        
        Args:
            config: Optional configuration dictionary for the factory.
        """
        if self._factory is not None:
            logger.warning("Service registry already initialized")
            return
            
        logger.info("Initializing service registry...")
        self._factory = ServiceFactory(config)
        self._factory.initialize_services()
        logger.info("Service registry initialized successfully")

    def get_service(self, service_type: type) -> Any:
        """
        Get a service by type.

        Args:
            service_type: Type of the service to retrieve.

        Returns:
            The requested service instance.

        Raises:
            RuntimeError: If the registry is not initialized.
        """
        if self._factory is None:
            raise RuntimeError("Service registry not initialized. Call initialize() first.")

        return self._factory.get_service(service_type)
    
    def is_initialized(self) -> bool:
        """
        Check if the registry is initialized.
        
        Returns:
            True if initialized, False otherwise.
        """
        return self._factory is not None and self._factory.is_initialized()
    
    # Modern service access methods using types
    @property
    def auth_service(self) -> IAuthService:
        """Get the authentication service."""
        return self.get_service(IAuthService)
    
    @property
    def repository(self) -> IRepository:
        """Get the repository."""
        return self.get_service(IRepository)
    
    @property
    def entity_service(self) -> IEntityService:
        """Get the entity service."""
        return self.get_service(IEntityService)
    
    @property
    def processor_manager(self) -> IProcessorManager:
        """Get the processor manager."""
        return self.get_service(IProcessorManager)
    
    @property
    def grpc_client(self) -> IGrpcClient:
        """Get the gRPC client."""
        return self.get_service(IGrpcClient)


# Global registry instance
_registry = ServiceRegistry()


def get_registry() -> ServiceRegistry:
    """
    Get the global service registry instance.
    
    Returns:
        The global ServiceRegistry instance.
    """
    return _registry


def initialize_services(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global service registry.
    
    Args:
        config: Optional configuration dictionary.
    """
    _registry.initialize(config)


def get_service(service_type: type) -> Any:
    """
    Get a service from the global registry by type.
    
    Args:
        service_type: Type of the service to retrieve.
        
    Returns:
        The requested service instance.
    """
    return _registry.get_service(service_type)


# Convenience functions for commonly used services
def get_auth_service() -> IAuthService:
    """Get the authentication service from the global registry."""
    return _registry.auth_service


def get_entity_service() -> IEntityService:
    """Get the entity service from the global registry."""
    return _registry.entity_service


def get_repository() -> IRepository:
    """Get the repository from the global registry."""
    return _registry.repository


def get_processor_manager() -> IProcessorManager:
    """Get the processor manager from the global registry."""
    return _registry.processor_manager


def get_grpc_client() -> IGrpcClient:
    """Get the gRPC client from the global registry."""
    return _registry.grpc_client
