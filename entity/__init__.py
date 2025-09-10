"""
Entity module for dynamic entity creation and management.

This module provides dynamic entity creation without requiring boilerplate factory code.
It automatically discovers and instantiates entity classes based on their names.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

from .cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)

# Cache for discovered entity classes
_entity_classes_cache: Dict[str, Type[CyodaEntity]] = {}
_cache_initialized = False


def _discover_entity_classes() -> Dict[str, Type[CyodaEntity]]:
    """
    Dynamically discover all entity classes in the entity module.

    Returns:
        Dictionary mapping entity names to their classes
    """
    global _entity_classes_cache, _cache_initialized

    if _cache_initialized:
        return _entity_classes_cache

    entity_classes = {}
    entity_dir = Path(__file__).parent

    # Scan all Python files in the entity directory
    for py_file in entity_dir.glob("*.py"):
        if py_file.name.startswith("__") or py_file.name == "cyoda_entity.py":
            continue

        module_name = py_file.stem
        try:
            # Import the module dynamically
            module = importlib.import_module(f"entity.{module_name}")

            # Find all classes that inherit from CyodaEntity
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    obj != CyodaEntity
                    and issubclass(obj, CyodaEntity)
                    and obj.__module__ == module.__name__
                ):

                    # Use both the class name and a lowercase version as keys
                    entity_classes[name] = obj
                    entity_classes[name.lower()] = obj

                    # Also use the ENTITY_NAME constant if available
                    if hasattr(obj, "ENTITY_NAME"):
                        entity_name = obj.ENTITY_NAME
                        entity_classes[entity_name] = obj
                        entity_classes[entity_name.lower()] = obj

                    logger.debug(f"Discovered entity class: {name} -> {obj}")

        except Exception as e:
            logger.warning(f"Failed to import entity module {module_name}: {e}")
            continue

    _entity_classes_cache = entity_classes
    _cache_initialized = True
    logger.info(f"Discovered {len(entity_classes)} entity class mappings")

    return entity_classes


def create_entity(entity_type: str, data: Dict[str, Any]) -> CyodaEntity:
    """
    Dynamically create an entity instance based on the entity type.

    Args:
        entity_type: The type/name of the entity to create
        data: The data to initialize the entity with

    Returns:
        An instance of the appropriate entity class

    Raises:
        ValueError: If the entity type is not found
    """
    entity_classes = _discover_entity_classes()

    # Try to find the entity class
    entity_class = entity_classes.get(entity_type)
    if not entity_class:
        # Try with different case variations
        entity_class = entity_classes.get(entity_type.lower())
    if not entity_class:
        entity_class = entity_classes.get(entity_type.upper())
    if not entity_class:
        entity_class = entity_classes.get(entity_type.capitalize())

    if not entity_class:
        available_types = list(set(entity_classes.keys()))
        raise ValueError(
            f"Unknown entity type: '{entity_type}'. "
            f"Available types: {available_types}"
        )

    try:
        # Create the entity instance
        entity = entity_class(**data)
        logger.debug(f"Created entity of type {entity_type}: {entity}")
        return entity
    except Exception as e:
        logger.error(f"Failed to create entity of type {entity_type}: {e}")
        raise ValueError(f"Failed to create entity of type '{entity_type}': {e}") from e


def get_entity_model(entity_type: str) -> Optional[Type[CyodaEntity]]:
    """
    Get the entity model class for a given entity type.

    Args:
        entity_type: The type/name of the entity

    Returns:
        The entity class or None if not found
    """
    entity_classes = _discover_entity_classes()

    # Try to find the entity class with different case variations
    for key_variant in [
        entity_type,
        entity_type.lower(),
        entity_type.upper(),
        entity_type.capitalize(),
    ]:
        if key_variant in entity_classes:
            return entity_classes[key_variant]

    return None


def get_available_entity_types() -> list[str]:
    """
    Get a list of all available entity types.

    Returns:
        List of available entity type names
    """
    entity_classes = _discover_entity_classes()
    # Return unique class names (not the lowercase variants)
    unique_types = set()
    for entity_class in entity_classes.values():
        if hasattr(entity_class, "ENTITY_NAME"):
            unique_types.add(entity_class.ENTITY_NAME)
        else:
            unique_types.add(entity_class.__name__)

    return sorted(unique_types)


def refresh_entity_cache() -> None:
    """
    Refresh the entity class cache. Useful for development or when new entities are added dynamically.
    """
    global _cache_initialized
    _cache_initialized = False
    _entity_classes_cache.clear()
    _discover_entity_classes()


# Export the main functions
__all__ = [
    "create_entity",
    "get_entity_model",
    "get_available_entity_types",
    "refresh_entity_cache",
    "CyodaEntity",
]
