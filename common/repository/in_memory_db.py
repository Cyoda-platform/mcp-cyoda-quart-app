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

import threading
import logging
from typing import List

from common.repository.crud_repository import CrudRepository
from common.utils.utils import *

logger = logging.getLogger('django')

# Global in-memory cache - this is where all data is stored when using in-memory repository
# This dictionary persists for the lifetime of the application process
cache = {}


class InMemoryRepository(CrudRepository):

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        logger.info("Initializing InMemoryRepository (singleton pattern)")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(InMemoryRepository, cls).__new__(cls)
                    logger.info("✓ InMemoryRepository singleton instance created")
                    logger.info("✓ Using global in-memory cache for data storage")
                    logger.info("⚠️  Data will NOT persist between application restarts")
        return cls._instance

    def __init__(self):
        """Initialize the in-memory repository."""
        if not hasattr(self, '_initialized'):
            logger.info("InMemoryRepository initialized successfully")
            logger.info(f"Current cache size: {len(cache)} entities")
            self._initialized = True

    async def get_transitions(self, meta, technical_id):
        pass

    async def get_meta(self, token, entity_model, entity_version):
        return {"token": token, "entity_model": entity_model, "entity_version": entity_version}

    async def count(self, meta) -> int:
        pass

    async def delete_all(self, meta) -> None:
        pass

    async def delete_all_entities(self, meta, entities: List[Any]) -> None:
        pass

    async def delete_all_by_key(self, meta, keys: List[Any]) -> None:
        pass

    async def delete_by_key(self, meta, key: Any) -> None:
        pass

    async def exists_by_key(self, meta, key: Any) -> bool:
        pass

    async def find_all(self, meta) -> List[Any]:
        pass

    async def find_all_by_key(self, meta, keys: List[Any]) -> List[Any]:
        pass

    async def find_by_key(self, meta, key: Any) -> Optional[Any]:
        pass

    async def find_by_id(self, meta, uuid: Any) -> Optional[Any]:
        return cache.get(uuid)

    async def find_all_by_criteria(self, meta, criteria: Any) -> Optional[Any]:
        entities = []
        for uuid in cache:
            if cache[uuid][criteria["key"]] == criteria["value"]:
                cache[uuid]['technical_id'] = uuid
                entities.append(cache[uuid])
        return entities

    async def save(self, meta, entity: Any) -> Any:
        uuid = str(generate_uuid())
        cache[uuid] = entity
        return uuid

    async def save_all(self, meta, entities: List[Any]) -> bool:
        pass

    async def update(self, meta, id, entity: Any) -> Any:
        cache[id] = entity
        return id

    async def update_all(self, meta, entities: List[Any]) -> List[Any]:
        pass

    async def delete(self, meta, entity: Any) -> None:
        pass

    async def delete_by_id(self, meta, technical_id: Any) -> None:
        del cache[technical_id]
