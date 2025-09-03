"""
Service module for application initialization and dependency injection.

This module provides a clean service factory pattern for managing application
dependencies and services.
"""

from .factory import ServiceFactory
from .registry import ServiceRegistry

__all__ = ['ServiceFactory', 'ServiceRegistry']
