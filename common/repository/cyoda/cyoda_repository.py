"""
Cyoda Repository Implementation

Thread-safe repository for interacting with the Cyoda API.
Provides CRUD operations with proper error handling and caching.
"""

import threading
import json
import logging
import time
import asyncio
from typing import List, Any, Optional, Dict

from common.config.config import CYODA_ENTITY_TYPE_EDGE_MESSAGE
from common.config.conts import EDGE_MESSAGE_CLASS, TREE_NODE_ENTITY_CLASS, UPDATE_TRANSITION
from common.repository.crud_repository import CrudRepository
from common.utils.utils import custom_serializer, send_cyoda_request

logger = logging.getLogger(__name__)

# In-memory cache for edge-message entities
_edge_messages_cache = {}


class CyodaRepository(CrudRepository):
    """
    Thread-safe singleton repository for interacting with the Cyoda API.
    Provides CRUD operations with caching and error handling.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, cyoda_auth_service):
        """Thread-safe singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cyoda_auth_service = cyoda_auth_service
        return cls._instance

    async def _wait_for_search_completion(
            self,
            snapshot_id: str,
            timeout: float = 60.0,
            interval: float = 0.3
    ) -> None:
        """Poll the snapshot status endpoint until SUCCESSFUL or error/timeout."""
        start = time.monotonic()
        status_path = f"search/snapshot/{snapshot_id}/status"

        while True:
            resp = await send_cyoda_request(
                cyoda_auth_service=self._cyoda_auth_service,
                method="get",
                path=status_path
            )
            if resp.get("status") != 200:
                return
            status = resp.get("json", {}).get("snapshotStatus")
            if status == "SUCCESSFUL":
                return
            if status not in ("RUNNING",):
                raise Exception(f"Snapshot search failed: {resp.get('json')}")
            if time.monotonic() - start > timeout:
                raise TimeoutError(f"Timeout exceeded after {timeout} seconds")
            await asyncio.sleep(interval)


    # CRUD Repository Implementation
    async def find_by_id(self, meta, entity_id: Any) -> Optional[Any]:
        """Find entity by ID."""
        if meta and meta.get("type") == CYODA_ENTITY_TYPE_EDGE_MESSAGE:
            if entity_id in _edge_messages_cache:
                return _edge_messages_cache[entity_id]
            path = f"message/get/{entity_id}"
            resp = await send_cyoda_request(
                cyoda_auth_service=self._cyoda_auth_service,
                method="get",
                path=path
            )
            content = resp.get("json", {}).get("content", "{}")
            data = json.loads(content).get("edge_message_content")
            if data:
                _edge_messages_cache[entity_id] = data
            return data

        path = f"entity/{entity_id}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="get",
            path=path
        )
        payload = resp.get("json", {})
        data = payload.get("data", {})
        data["current_state"] = payload.get("meta", {}).get("state")
        data["technical_id"] = entity_id
        return data

    async def find_all(self, meta) -> List[Any]:
        """Find all entities of a specific model."""
        path = f"entity/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="get",
            path=path
        )
        return resp.get("json", [])

    async def find_all_by_criteria(self, meta, criteria: Any) -> List[Any]:
        """Find entities matching specific criteria using snapshot search."""
        # 1. Create snapshot
        snap_path = f"search/snapshot/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="post",
            path=snap_path,
            data=json.dumps(criteria)
        )
        snapshot_id = resp.get("json")

        # 2. Wait for completion
        await self._wait_for_search_completion(snapshot_id)

        # 3. Fetch results
        result_resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="get",
            path=f"search/snapshot/{snapshot_id}"
        )
        if result_resp.get("status") != 200:
            return []
        resp_json = json.loads(result_resp.get("json", "{}"))

        if resp_json.get("page", {}).get("totalElements", 0) == 0:
            return []

        nodes = resp_json.get("_embedded", {}).get("objectNodes", [])
        entities = []
        for node in nodes:
            tree = node.get("data", {})
            if not tree.get("technical_id"):
                tree["technical_id"] = node.get("meta", {}).get("id")
            entities.append(tree)

        return entities

    async def save(self, meta, entity: Any) -> Any:
        """Save a single entity."""
        if meta.get("type") == CYODA_ENTITY_TYPE_EDGE_MESSAGE:
            payload = {
                "meta-data": {"source": "cyoda_client"},
                "payload": {"edge_message_content": entity},
            }
            data = json.dumps(payload, default=custom_serializer)
            path = f"message/new/{meta['entity_model']}_{meta['entity_version']}"
        else:
            data = json.dumps(entity, default=custom_serializer)
            path = f"entity/JSON/{meta['entity_model']}/{meta['entity_version']}"

        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="post",
            path=path,
            data=data
        )
        result = resp.get("json", [])

        technical_id = None
        if isinstance(result, list) and result:
            technical_id = result[0].get("entityIds", [None])[0]

        if meta.get("type") == CYODA_ENTITY_TYPE_EDGE_MESSAGE and technical_id:
            _edge_messages_cache[technical_id] = entity

        return technical_id

    async def save_all(self, meta, entities: List[Any]) -> Any:
        """Save multiple entities in batch."""
        data = json.dumps(entities, default=custom_serializer)
        path = f"entity/JSON/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="post",
            path=path,
            data=data
        )
        result = resp.get("json", [])

        technical_id = None
        if isinstance(result, list) and result:
            technical_id = result[0].get("entityIds", [None])[0]

        return technical_id

    async def update(self, meta, technical_id: Any, entity: Any = None) -> Any:
        """Update an entity or launch a transition."""
        if entity is None:
            return await self._launch_transition(meta=meta, technical_id=technical_id)

        transition = meta.get("update_transition", UPDATE_TRANSITION)
        path = (
            f"entity/JSON/{technical_id}/{transition}"
            "?transactional=true&waitForConsistencyAfter=true"
        )
        data = json.dumps(entity, default=custom_serializer)
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="put",
            path=path,
            data=data
        )
        result = resp.get("json", {})
        if not isinstance(result, dict):
            logger.exception(result)
            return None
        return result.get("entityIds", [None])[0]

    async def delete_by_id(self, meta, technical_id: Any) -> None:
        """Delete entity by ID."""
        path = f"entity/{technical_id}"
        await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="delete",
            path=path
        )

    async def count(self, meta) -> int:
        """Count entities of a specific model."""
        items = await self.find_all(meta)
        return len(items)

    async def exists_by_key(self, meta, key: Any) -> bool:
        """Check if entity exists by key."""
        return (await self.find_by_key(meta, key)) is not None

    async def find_by_key(self, meta, key: Any) -> Optional[Any]:
        """Find entity by key."""
        criteria = meta.get("condition") or {"key": key}
        entities = await self.find_all_by_criteria(meta, criteria)
        return entities[0] if entities else None

    async def delete_all(self, meta) -> None:
        """Delete all entities of a specific model."""
        path = f"entity/{meta['entity_model']}/{meta['entity_version']}"
        await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="delete",
            path=path
        )

    async def get_meta(self, token, entity_model, entity_version):
        """Get metadata for repository operations."""
        return {
            "token": token,
            "entity_model": entity_model,
            "entity_version": entity_version
        }

    async def _launch_transition(self, meta, technical_id):
        """Launch entity transition."""
        entity_class = (
            EDGE_MESSAGE_CLASS
            if meta.get("type") == CYODA_ENTITY_TYPE_EDGE_MESSAGE
            else TREE_NODE_ENTITY_CLASS
        )
        path = (
            f"platform-api/entity/transition?entityId={technical_id}"
            f"&entityClass={entity_class}&transitionName="
            f"{meta.get('update_transition', UPDATE_TRANSITION)}"
        )
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="put",
            path=path
        )
        if resp.get('status') != 200:
            raise Exception(resp.get('json'))
        return resp.get("json")
