"""
Dynamic Entity Factory for Cyoda entities.

This module provides a simple, configuration-free approach to entity creation.
All entities are created as CyodaEntity instances, and specific typing is handled
at the implementation level through dynamic casting.
"""

import logging
from typing import Any, Dict

from common.entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


def create_entity(entity_type: str, data: Dict[str, Any]) -> CyodaEntity:
    """
    Create a CyodaEntity instance with the provided data.

    This function always creates a generic CyodaEntity instance, regardless of the
    entity_type parameter. Specific entity behavior is handled through dynamic
    casting at the implementation level (processors, criteria, etc.).

    Args:
        entity_type: The type/name of the entity (used for logging only)
        data: The data to initialize the entity with

    Returns:
        A CyodaEntity instance with the provided data

    Raises:
        ValueError: If entity creation fails
    """
    try:
        # Always create a generic CyodaEntity - no registration needed
        entity = CyodaEntity(**data)
        logger.debug(f"Created CyodaEntity for type '{entity_type}': {entity}")
        return entity
    except Exception as e:
        logger.error(f"Failed to create entity of type '{entity_type}': {e}")
        raise ValueError(f"Failed to create entity of type '{entity_type}': {e}") from e
