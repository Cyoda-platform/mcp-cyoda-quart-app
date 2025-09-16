"""
Cat Fact Subscription Application.

This package contains the complete implementation of the cat fact subscription system
including entities, processors, criteria, and routes.
"""

__all__ = ["initialize_application_components"]


def initialize_application_components(app):
    """Initialize application components lazily."""
    from .app import initialize_application_components as _init
    return _init(app)
