"""
Entity factory for creating entity instances dynamically.
"""
from typing import Dict, Any, Type
from .cyoda_entity import CyodaEntity
from .mail import MailEntity
from .job import JobEntity


# Entity type mapping for factory pattern
ENTITY_MODELS: Dict[str, Type[CyodaEntity]] = {
    'mail': MailEntity,
    'job': JobEntity,

}


def create_entity(entity_type: str, data: Dict[str, Any]) -> CyodaEntity:
    """Factory function to create entity instances"""
    if entity_type not in ENTITY_MODELS:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    entity_class = ENTITY_MODELS[entity_type]
    return entity_class(**data)


def get_entity_model(entity_type: str) -> Type[CyodaEntity]:
    """Get entity model class by type"""
    if entity_type not in ENTITY_MODELS:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    return ENTITY_MODELS[entity_type]


def get_available_entity_types() -> list[str]:
    """Get list of available entity types"""
    return list(ENTITY_MODELS.keys())


def register_entity_model(entity_type: str, model_class: Type[CyodaEntity]) -> None:
    """Register a new entity model type"""
    if not issubclass(model_class, CyodaEntity):
        raise ValueError(f"Model class must inherit from CyodaEntity")
    
    ENTITY_MODELS[entity_type] = model_class
