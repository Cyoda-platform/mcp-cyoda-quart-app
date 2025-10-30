"""
In-Memory Repository Implementation

This module provides an in-memory repository implementation using a global dictionary cache.
The in-memory database is used when CHAT_REPOSITORY environment variable is not set to 'cyoda'.

IMPORTANT:
- This is a global in-memory cache that persists for the lifetime of the application
- Data is NOT persisted between application restarts
- This is primarily used for testing and development
- The cache is thread-safe using singleton pattern with locks

Configuration:
- Set CHAT_REPOSITORY=cyoda to use Cyoda repository instead
- Set CHAT_REPOSITORY=in_memory (or leave unset) to use this in-memory repository
"""

import logging
import threading
from typing import Any, Dict, List, Optional

from common.repository.crud_repository import CrudRepository
from common.utils.utils import generate_uuid

logger = logging.getLogger(__name__)

# Global in-memory cache - this is where all data is stored when using in-memory repository
# This dictionary persists for the lifetime of the application process
cache: Dict[str, Any] = {}


class InMemoryRepository(CrudRepository[Any]):
    _instance: Optional["InMemoryRepository"] = None
    _lock = threading.Lock()
    _cache_lock = threading.RLock()

    def __new__(cls) -> "InMemoryRepository":
        logger.info("Initializing InMemoryRepository (singleton pattern)")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(InMemoryRepository, cls).__new__(cls)
                    logger.info("✓ InMemoryRepository singleton instance created")
                    logger.info("✓ Using global in-memory cache for data storage")
                    logger.info("⚠️  Data will NOT persist between application restarts")
        return cls._instance

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        if not hasattr(self, "_initialized"):
            logger.info("InMemoryRepository initialized successfully")
            logger.info(f"Current cache size: {len(cache)} entities")
            self._initialized = True

    # ---- Domain / workflow helpers -------------------------------------------------

    async def get_transitions(self, meta: Dict[str, Any], technical_id: Any) -> Any:
        # No state-machine logic in the in-memory impl; return empty list for safety.
        return []

    async def get_meta(
        self, token: str, entity_model: str, entity_version: str
    ) -> Dict[str, Any]:
        return {
            "token": token,
            "entity_model": entity_model,
            "entity_version": entity_version,
        }

    # ---- CRUD operations ------------------------------------------------------------

    async def count(self, meta: Dict[str, Any]) -> int:
        with self._cache_lock:
            return len(cache)

    async def delete_all(self, meta: Dict[str, Any]) -> None:
        with self._cache_lock:
            cache.clear()

    async def delete_all_entities(
        self, meta: Dict[str, Any], entities: List[Any]
    ) -> None:
        """
        Best-effort deletion:
        - If an item is a dict with 'technical_id', delete by that id.
        - Else if the item is a key present in cache, delete by key.
        - Else try to remove by value (O(n)).
        """
        with self._cache_lock:
            for item in entities:
                # Case 1: dict-like entity with technical_id
                if isinstance(item, dict) and "technical_id" in item:
                    cache.pop(item["technical_id"], None)
                    continue
                # Case 2: treat item as a key
                if item in cache:
                    cache.pop(item, None)
                    continue
                # Case 3: remove by value
                # (build list to avoid RuntimeError: dict changed size during iteration)
                to_delete = [k for k, v in cache.items() if v == item]
                for k in to_delete:
                    cache.pop(k, None)

    async def delete_all_by_key(self, meta: Dict[str, Any], keys: List[Any]) -> None:
        with self._cache_lock:
            for k in keys:
                cache.pop(k, None)

    async def delete_by_key(self, meta: Dict[str, Any], key: Any) -> None:
        with self._cache_lock:
            cache.pop(key, None)

    async def exists_by_key(self, meta: Dict[str, Any], key: Any) -> bool:
        with self._cache_lock:
            return key in cache

    async def find_all(self, meta: Dict[str, Any]) -> List[Any]:
        with self._cache_lock:
            return list(cache.values())

    async def find_all_by_key(self, meta: Dict[str, Any], keys: List[Any]) -> List[Any]:
        with self._cache_lock:
            return [cache[k] for k in keys if k in cache]

    async def find_by_key(self, meta: Dict[str, Any], key: Any) -> Optional[Any]:
        with self._cache_lock:
            return cache.get(key)

    async def find_by_id(
        self,
        meta: Dict[str, Any],
        entity_id: Any,
        point_in_time: Optional[Any] = None,
    ) -> Optional[Any]:
        with self._cache_lock:
            return cache.get(entity_id)

    async def find_all_by_criteria(
        self, meta: Dict[str, Any], criteria: Any, point_in_time: Optional[Any] = None
    ) -> List[Any]:
        """
        Very simple filtering:
        - Expects criteria like {"key": "<field>", "value": <value>}
        - If entity is dict-like, compare on that key
        """
        key = criteria.get("key")
        value = criteria.get("value")
        if key is None:
            return []
        results: List[Any] = []
        with self._cache_lock:
            for uuid, entity in cache.items():
                try:
                    if isinstance(entity, dict) and entity.get(key) == value:
                        # Attach technical_id for convenience (non-destructive copy)
                        item = dict(entity)
                        item["technical_id"] = uuid
                        results.append(item)
                except Exception:
                    # Ignore entities that don't support the lookup pattern
                    continue
        return results

    async def save(self, meta: Dict[str, Any], entity: Any) -> Any:
        with self._cache_lock:
            uuid = str(generate_uuid())
            cache[uuid] = entity
            return uuid

    async def save_all(self, meta: Dict[str, Any], entities: List[Any]) -> bool:
        with self._cache_lock:
            for entity in entities:
                uuid = str(generate_uuid())
                cache[uuid] = entity
        return True

    async def update(
        self, meta: Dict[str, Any], entity_id: Any, entity: Any | None = None
    ) -> Any:
        """
        Update the entity stored at entity_id.
        If entity is None, this is a no-op (returns the id if it exists, else creates None).
        """
        with self._cache_lock:
            if entity is not None:
                cache[entity_id] = entity
            # If entity is None, we don't mutate; still return the id for consistency
            return entity_id

    async def update_all(self, meta: Dict[str, Any], entities: List[Any]) -> List[Any]:
        """
        Best-effort bulk update.
        Accepts either:
        - A list of dicts that contain 'technical_id' and the rest of the entity payload, or
        - A list of (id, entity) tuples.
        Returns the list of ids that were updated/inserted.
        """
        updated_ids: List[Any] = []
        with self._cache_lock:
            for item in entities:
                if isinstance(item, dict) and "technical_id" in item:
                    tid = item["technical_id"]
                    entity = {k: v for k, v in item.items() if k != "technical_id"}
                    cache[tid] = entity
                    updated_ids.append(tid)
                elif isinstance(item, tuple) and len(item) == 2:
                    tid, entity = item
                    cache[tid] = entity
                    updated_ids.append(tid)
                else:
                    # If it's a plain entity, treat as save and generate a new id
                    tid = str(generate_uuid())
                    cache[tid] = item
                    updated_ids.append(tid)
        return updated_ids

    async def delete(self, meta: Dict[str, Any], entity: Any) -> None:
        """
        Delete by:
        - entity['technical_id'] if present, else
        - by value match (first match).
        """
        with self._cache_lock:
            if isinstance(entity, dict) and "technical_id" in entity:
                cache.pop(entity["technical_id"], None)
                return
            # Fallback: remove by value (first match)
            for k, v in list(cache.items()):
                if v == entity:
                    cache.pop(k, None)
                    break

    async def delete_by_id(self, meta: Dict[str, Any], technical_id: Any) -> None:
        with self._cache_lock:
            cache.pop(technical_id, None)

    async def get_entity_count(
        self, meta: Dict[str, Any], point_in_time: Optional[Any] = None
    ) -> int:
        """
        Get count of entities for a specific model.
        In-memory implementation ignores point_in_time since we don't track history.
        """
        with self._cache_lock:
            return len(cache)

    async def get_entity_changes_metadata(
        self, entity_id: Any, point_in_time: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Get entity change history metadata.
        In-memory implementation doesn't track change history, returns empty list.
        """
        return []
