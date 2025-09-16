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

# Import Purrfect Pets API blueprints
try:
    from application.routes.pets import pets_bp
    from application.routes.owners import owners_bp
    from application.routes.orders import orders_bp
    from application.routes.categories import categories_bp
    PURRFECT_PETS_AVAILABLE = True
except ImportError:
    PURRFECT_PETS_AVAILABLE = False
    pets_bp = owners_bp = orders_bp = categories_bp = None

# Export all blueprints for easy import
__all__ = [
    'jobs_bp',
    'laureates_bp',
    'subscribers_bp',
    'health_bp',
    'system_bp'
]

# Add Purrfect Pets blueprints if available
if PURRFECT_PETS_AVAILABLE:
    __all__.extend(['pets_bp', 'owners_bp', 'orders_bp', 'categories_bp'])