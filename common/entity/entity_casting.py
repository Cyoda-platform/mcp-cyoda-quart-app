"""
Dynamic entity casting utilities.

This module provides utilities for dynamically casting CyodaEntity instances
to specific entity types at runtime, enabling type-safe operations without
requiring upfront registration or configuration.
"""

import importlib
import logging
from typing import Any, Dict, Optional, Type, TypeVar, cast

from common.entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=CyodaEntity)


def cast_entity(entity: CyodaEntity, target_type: Type[T]) -> T:
    """
    Cast a CyodaEntity to a specific entity type.

    This function attempts to create a new instance of the target type using
    the data from the source entity. If the casting fails, it returns the
    original entity cast to the target type (duck typing).

    Args:
        entity: The source CyodaEntity instance
        target_type: The target entity class to cast to

    Returns:
        An instance of the target type with the entity's data

    Raises:
        TypeError: If the target_type is not a subclass of CyodaEntity
    """
    if not issubclass(target_type, CyodaEntity):
        raise TypeError(f"Target type {target_type} must be a subclass of CyodaEntity")

    # If already the correct type, return as-is
    if isinstance(entity, target_type):
        return entity

    try:
        # Try to create a new instance of the target type with the entity's data
        entity_data = (
            entity.model_dump() if hasattr(entity, "model_dump") else entity.dict()
        )
        casted_entity = target_type(**entity_data)
        logger.debug(
            f"Successfully cast {type(entity).__name__} to {target_type.__name__}"
        )
        return casted_entity
    except Exception as e:
        logger.warning(
            f"Failed to cast {type(entity).__name__} to {target_type.__name__}: {e}"
        )
        # Fallback: return the original entity cast to the target type (duck typing)
        return cast(T, entity)


def try_cast_entity(entity: CyodaEntity, target_type: Type[T]) -> Optional[T]:
    """
    Attempt to cast a CyodaEntity to a specific entity type, returning None on failure.

    Args:
        entity: The source CyodaEntity instance
        target_type: The target entity class to cast to

    Returns:
        An instance of the target type, or None if casting fails
    """
    try:
        return cast_entity(entity, target_type)
    except Exception as e:
        logger.debug(
            f"Cast attempt failed for {type(entity).__name__} to {target_type.__name__}: {e}"
        )
        return None


def dynamic_import_entity_class(
    entity_name: str, module_paths: list[str]
) -> Optional[Type[CyodaEntity]]:
    """
    Dynamically import an entity class by name from a list of possible module paths.

    Args:
        entity_name: The name of the entity class to import
        module_paths: List of module paths to search for the entity class

    Returns:
        The entity class if found, None otherwise
    """
    for module_path in module_paths:
        try:
            # Try to import the module
            module = importlib.import_module(module_path)

            # Look for the entity class in the module
            if hasattr(module, entity_name):
                entity_class = getattr(module, entity_name)
                if isinstance(entity_class, type) and issubclass(
                    entity_class, CyodaEntity
                ):
                    logger.debug(f"Found entity class {entity_name} in {module_path}")
                    return entity_class
        except ImportError as e:
            logger.debug(f"Could not import {module_path}: {e}")
            continue
        except Exception as e:
            logger.warning(
                f"Error while searching for {entity_name} in {module_path}: {e}"
            )
            continue

    logger.debug(
        f"Entity class {entity_name} not found in any of the provided module paths"
    )
    return None


def smart_cast_entity(
    entity: CyodaEntity,
    entity_type_hint: str,
    search_modules: Optional[list[str]] = None,
) -> CyodaEntity:
    """
    Intelligently cast an entity based on a type hint string.

    This function attempts to find and import the appropriate entity class
    based on the entity_type_hint, then cast the entity to that type.

    Args:
        entity: The source CyodaEntity instance
        entity_type_hint: String hint about the entity type (e.g., "ExampleEntity", "exampleentity")
        search_modules: Optional list of module paths to search for entity classes

    Returns:
        The cast entity, or the original entity if casting is not possible
    """
    if search_modules is None:
        # Default search paths for entity classes
        search_modules = [
            "example_application.entity.example_entity",
            "example_application.entity.other_entity",
            "application.entity.example_entity",
            "application.entity.other_entity",
        ]

    # Generate possible class names from the hint
    possible_class_names = [
        entity_type_hint,
        entity_type_hint.capitalize(),
        entity_type_hint.title(),
        f"{entity_type_hint.capitalize()}Entity",
        f"{entity_type_hint.title()}Entity",
    ]

    # Try to find and import the entity class
    for class_name in possible_class_names:
        entity_class = dynamic_import_entity_class(class_name, search_modules)
        if entity_class:
            try:
                return cast_entity(entity, entity_class)
            except Exception as e:
                logger.debug(f"Failed to cast to {class_name}: {e}")
                continue

    # If no specific type found, return the original entity
    logger.debug(
        f"Could not find specific entity class for '{entity_type_hint}', using generic CyodaEntity"
    )
    return entity


def get_entity_type_from_data(data: Dict[str, Any]) -> str:
    """
    Extract entity type information from entity data.

    Args:
        data: Entity data dictionary

    Returns:
        String representing the entity type, or "unknown" if not determinable
    """
    # Look for common entity type indicators in the data
    type_indicators = [
        "entity_type",
        "entityType",
        "type",
        "__type__",
        "_type",
        "model_type",
        "modelType",
    ]

    for indicator in type_indicators:
        if indicator in data and data[indicator]:
            return str(data[indicator])

    # If no explicit type indicator, try to infer from field patterns
    if "category" in data and "value" in data and "isActive" in data:
        return "ExampleEntity"
    elif "title" in data and "content" in data and "priority" in data:
        return "OtherEntity"

    return "unknown"
