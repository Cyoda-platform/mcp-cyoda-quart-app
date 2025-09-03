"""
Modern Service Factory using dependency-injector.

This module provides a clean factory for creating and managing
application services using the dependency-injector framework.
"""

import logging
from typing import Dict, Any, Optional

from .container import ServiceContainer, get_container

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Modern service factory using dependency-injector container.
    
    This factory provides a clean interface to the dependency injection system.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the service factory with optional configuration.

        Args:
            config: Optional configuration dictionary.
        """
        self.container = get_container()
        if config:
            self.container.configure(config)
        
        self._initialized = False
    
    def initialize_services(self) -> None:
        """Initialize all services with dependency injection."""
        if self._initialized:
            logger.warning("Services already initialized")
            return

        self.container.initialize()
        self._initialized = True
        logger.info("Services initialized successfully")

    def get_service(self, service_type: type) -> Any:
        """
        Get a service by type.

        Args:
            service_type: Type of the service to retrieve.

        Returns:
            The requested service instance.
        """
        if not self._initialized:
            self.initialize_services()

        return self.container.get_service(service_type)

    def is_initialized(self) -> bool:
        """
        Check if services have been initialized.
        
        Returns:
            True if services are initialized, False otherwise.
        """
        return self._initialized
