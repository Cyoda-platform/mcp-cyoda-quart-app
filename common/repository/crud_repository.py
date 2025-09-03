"""
CRUD Repository Interface

This module defines the abstract base class for CRUD operations
following repository pattern best practices.
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict, TypeVar, Generic

# Generic type for entity
T = TypeVar('T')


class CrudRepository(ABC, Generic[T]):
    """
    Abstract base class for CRUD repository operations.
    
    This interface defines the standard CRUD operations that all
    repository implementations should provide.
    """

    @abstractmethod
    async def find_by_id(self, meta: Dict[str, Any], entity_id: Any) -> Optional[T]:
        """
        Find entity by ID.
        
        Args:
            meta: Metadata containing entity model information
            entity_id: Unique identifier of the entity
            
        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_all(self, meta: Dict[str, Any]) -> List[T]:
        """
        Find all entities of a specific model.
        
        Args:
            meta: Metadata containing entity model information
            
        Returns:
            List of all entities
        """
        pass

    @abstractmethod
    async def find_all_by_criteria(self, meta: Dict[str, Any], criteria: Any) -> List[T]:
        """
        Find entities matching specific criteria.
        
        Args:
            meta: Metadata containing entity model information
            criteria: Search criteria
            
        Returns:
            List of matching entities
        """
        pass

    @abstractmethod
    async def save(self, meta: Dict[str, Any], entity: T) -> Any:
        """
        Save a single entity.
        
        Args:
            meta: Metadata containing entity model information
            entity: Entity to save
            
        Returns:
            Entity ID or saved entity
        """
        pass

    @abstractmethod
    async def save_all(self, meta: Dict[str, Any], entities: List[T]) -> Any:
        """
        Save multiple entities.
        
        Args:
            meta: Metadata containing entity model information
            entities: List of entities to save
            
        Returns:
            List of entity IDs or saved entities
        """
        pass

    @abstractmethod
    async def update(self, meta: Dict[str, Any], entity_id: Any, entity: T = None) -> Any:
        """
        Update an entity.
        
        Args:
            meta: Metadata containing entity model information
            entity_id: ID of entity to update
            entity: Updated entity data (optional for transitions)
            
        Returns:
            Updated entity ID or entity
        """
        pass

    @abstractmethod
    async def delete_by_id(self, meta: Dict[str, Any], entity_id: Any) -> None:
        """
        Delete entity by ID.
        
        Args:
            meta: Metadata containing entity model information
            entity_id: ID of entity to delete
        """
        pass

    @abstractmethod
    async def count(self, meta: Dict[str, Any]) -> int:
        """
        Count entities of a specific model.
        
        Args:
            meta: Metadata containing entity model information
            
        Returns:
            Number of entities
        """
        pass

    @abstractmethod
    async def exists_by_key(self, meta: Dict[str, Any], key: Any) -> bool:
        """
        Check if entity exists by key.
        
        Args:
            meta: Metadata containing entity model information
            key: Key to check
            
        Returns:
            True if entity exists, False otherwise
        """
        pass

    # Optional methods with default implementations
    async def find_by_key(self, meta: Dict[str, Any], key: Any) -> Optional[T]:
        """
        Find entity by key.
        
        Args:
            meta: Metadata containing entity model information
            key: Key to search for
            
        Returns:
            Entity if found, None otherwise
        """
        criteria = meta.get("condition") or {"key": key}
        entities = await self.find_all_by_criteria(meta, criteria)
        return entities[0] if entities else None

    async def find_all_by_key(self, meta: Dict[str, Any], keys: List[Any]) -> List[T]:
        """
        Find entities by multiple keys.
        
        Args:
            meta: Metadata containing entity model information
            keys: List of keys to search for
            
        Returns:
            List of matching entities
        """
        results = []
        for key in keys:
            entity = await self.find_by_key(meta, key)
            if entity:
                results.append(entity)
        return results

    async def delete_all(self, meta: Dict[str, Any]) -> None:
        """
        Delete all entities of a specific model.
        
        Args:
            meta: Metadata containing entity model information
        """
        entities = await self.find_all(meta)
        for entity in entities:
            entity_id = getattr(entity, 'technical_id', entity.get('technical_id') if isinstance(entity, dict) else None)
            if entity_id:
                await self.delete_by_id(meta, entity_id)

    async def delete_all_entities(self, meta: Dict[str, Any], entities: List[T]) -> None:
        """
        Delete multiple specific entities.
        
        Args:
            meta: Metadata containing entity model information
            entities: List of entities to delete
        """
        for entity in entities:
            entity_id = getattr(entity, 'technical_id', entity.get('technical_id') if isinstance(entity, dict) else None)
            if entity_id:
                await self.delete_by_id(meta, entity_id)

    async def delete_all_by_key(self, meta: Dict[str, Any], keys: List[Any]) -> None:
        """
        Delete entities by multiple keys.
        
        Args:
            meta: Metadata containing entity model information
            keys: List of keys for entities to delete
        """
        for key in keys:
            await self.delete_by_key(meta, key)

    async def delete_by_key(self, meta: Dict[str, Any], key: Any) -> None:
        """
        Delete entity by key.
        
        Args:
            meta: Metadata containing entity model information
            key: Key of entity to delete
        """
        entity = await self.find_by_key(meta, key)
        if entity:
            entity_id = getattr(entity, 'technical_id', entity.get('technical_id') if isinstance(entity, dict) else None)
            if entity_id:
                await self.delete_by_id(meta, entity_id)

    async def update_all(self, meta: Dict[str, Any], entities: List[T]) -> List[T]:
        """
        Update multiple entities.
        
        Args:
            meta: Metadata containing entity model information
            entities: List of entities to update
            
        Returns:
            List of updated entities
        """
        updated_entities = []
        for entity in entities:
            entity_id = getattr(entity, 'technical_id', entity.get('technical_id') if isinstance(entity, dict) else None)
            if entity_id:
                updated_entity = await self.update(meta, entity_id, entity)
                updated_entities.append(updated_entity)
        return updated_entities

    async def get_meta(self, token: str, entity_model: str, entity_version: str) -> Dict[str, Any]:
        """
        Get metadata for repository operations.
        
        Args:
            token: Authentication token
            entity_model: Entity model name
            entity_version: Entity model version
            
        Returns:
            Metadata dictionary
        """
        return {
            "token": token,
            "entity_model": entity_model,
            "entity_version": entity_version
        }
