"""
Routes package for the Quart client application.

This package contains organized route modules for different functionalities:
- jobs: Job scheduling and management
- laureates: Nobel laureate operations
- subscribers: Subscriber management
- health: Health checks and monitoring
- mcp: FastMCP integration
- system: System information and metrics
"""

from .jobs import jobs_bp
from .laureates import laureates_bp
from .subscribers import subscribers_bp
from .health import health_bp
from .system import system_bp

# Export all blueprints for easy import
__all__ = [
    'jobs_bp',
    'laureates_bp',
    'subscribers_bp',
    'health_bp',
    'system_bp'
]