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
        """Find entities matching specific criteria using direct search endpoint."""
        # Use direct search endpoint: POST /search/{entityName}/{modelVersion}
        search_path = f"search/{meta['entity_model']}/{meta['entity_version']}"

        # Convert criteria to Cyoda-native format if needed
        search_criteria = self._ensure_cyoda_format(criteria)

        resp = await self._send_search_request(
            method="post",
            path=search_path,
            data=json.dumps(search_criteria)
        )

        if resp.get("status") != 200:
            return []

        # Handle the response - it should be a list of entities
        entities = resp.get("json", [])
        if not isinstance(entities, list):
            return []

        # Ensure each entity has technical_id
        for entity in entities:
            if isinstance(entity, dict) and not entity.get("technical_id"):
                # Try to get technical_id from meta or other fields
                if "meta" in entity and "id" in entity["meta"]:
                    entity["technical_id"] = entity["meta"]["id"]
                elif "id" in entity:
                    entity["technical_id"] = entity["id"]

        return entities

    async def _send_search_request(
        self,
        method: str,
        path: str,
        data: str = None,
        base_url: str = None
    ) -> dict:
        """
        Send a search request to the Cyoda API with custom headers and automatic retry on 401.
        """
        from common.utils.utils import send_request
        from common.config.config import CYODA_API_URL

        if base_url is None:
            base_url = CYODA_API_URL

        token = await self._cyoda_auth_service.get_access_token()

        for attempt in range(2):
            try:
                # Prepare headers for search endpoint
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}" if not token.startswith('Bearer') else token,
                }

                url = f"{base_url}/{path}"

                # Send request
                response = await send_request(headers, url, method, data=data)

            except Exception as exc:
                msg = str(exc)
                if attempt == 0 and ("401" in msg or "Unauthorized" in msg):
                    logger.warning(f"Request to {path} failed with 401; invalidating tokens and retrying")
                    self._cyoda_auth_service.invalidate_tokens()
                    token = await self._cyoda_auth_service.get_access_token()
                    continue
                raise

            status = response.get("status") if isinstance(response, dict) else None
            if attempt == 0 and status == 401:
                logger.warning(f"Response from {path} returned status 401; invalidating tokens and retrying")
                self._cyoda_auth_service.invalidate_tokens()
                token = await self._cyoda_auth_service.get_access_token()
                continue
            return response

        raise RuntimeError(f"Failed request {method.upper()} {path} after retry")

    def _ensure_cyoda_format(self, criteria: Any) -> dict:
        """Ensure criteria is in Cyoda-native format."""
        if not isinstance(criteria, dict):
            return criteria

        # If it's already in group format, return as-is
        if criteria.get("type") == "group":
            return criteria

        # If it's a single condition (simple or lifecycle), wrap it in a group
        if criteria.get("type") in ["simple", "lifecycle"]:
            return {
                "type": "group",
                "operator": "AND",
                "conditions": [criteria]
            }

        # If it's a simple field-value dictionary, convert to Cyoda group format
        conditions = []
        for field, value in criteria.items():
            if field in ["state", "current_state"]:
                conditions.append({
                    "type": "lifecycle",
                    "field": field,
                    "operatorType": "EQUALS",
                    "value": value
                })
            else:
                # Handle complex field-operator-value format
                if isinstance(value, dict) and len(value) == 1:
                    # Format: {"field": {"operator": "value"}}
                    operator, actual_value = next(iter(value.items()))

                    # Map internal operators back to Cyoda operators
                    operator_mapping = {
                        "eq": "EQUALS",
                        "ieq": "IEQUALS",
                        "ne": "NOT_EQUALS",
                        "contains": "CONTAINS",
                        "icontains": "ICONTAINS",
                        "gt": "GREATER_THAN",
                        "lt": "LESS_THAN",
                        "gte": "GREATER_THAN_OR_EQUAL",
                        "lte": "LESS_THAN_OR_EQUAL",
                        "startswith": "STARTS_WITH",
                        "endswith": "ENDS_WITH",
                        "in": "IN",
                        "not_in": "NOT_IN"
                    }

                    cyoda_operator = operator_mapping.get(operator, "EQUALS")

                    # Convert field to jsonPath format
                    json_path = f"$.{field}" if not field.startswith("$.") else field
                    conditions.append({
                        "type": "simple",
                        "jsonPath": json_path,
                        "operatorType": cyoda_operator,
                        "value": actual_value
                    })
                else:
                    # Simple field-value format: {"field": "value"}
                    json_path = f"$.{field}" if not field.startswith("$.") else field
                    conditions.append({
                        "type": "simple",
                        "jsonPath": json_path,
                        "operatorType": "EQUALS",
                        "value": value
                    })

        return {
            "type": "group",
            "operator": "AND",
            "conditions": conditions
        }



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
