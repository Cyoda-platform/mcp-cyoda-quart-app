"""
Entity module containing all entity models and base classes.
"""

from .cyoda_entity import CyodaEntity
from .job import JobEntity


def create_entity(entity_type: str = "default", **kwargs):
    """Create an entity based on type."""
    if entity_type == "job":
        return JobEntity(**kwargs)
    else:
        return CyodaEntity(**kwargs)


def get_entity_model(entity_type: str = "default"):
    """Get entity model class based on type."""
    if entity_type == "job":
        return JobEntity
    else:
        return CyodaEntity
