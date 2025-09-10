"""
Routes module for the Cyoda Client Application.

This module exports all available blueprints for the application.
"""

from .health import health_bp
from .system import system_bp

__all__ = ["health_bp", "system_bp"]
