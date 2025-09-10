"""
Application Entity Module - Redirect to Example Application

This module redirects to the example_application.entity module for backward compatibility.
Users should update their imports to use example_application.entity directly.
"""

# Import all functions from example_application.entity for backward compatibility
from example_application.entity import *  # noqa: F403, F401

# Explicitly import the main functions that are commonly used
from example_application.entity import create_entity, get_entity_class  # noqa: F401
