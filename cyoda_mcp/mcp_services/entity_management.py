"""
Entity Management Service for MCP

This service provides entity management functionality for the MCP server,
using the existing dependency injection system.
"""

import logging
from typing import Any, Dict

from common.config.config import ENTITY_VERSION
from common.service.entity_service import (
    CYODA_OPERATOR_MAPPING,
    EntityService,
    LogicalOperator,
    SearchConditionRequest,
    SearchOperator,
)

logger = logging.getLogger(__name__)


class EntityManagementService:
    """Service class for entity management operations."""

    def __init__(self, entity_service: EntityService):
        """
        Initialize the entity management service.

        Args:
            entity_service: The injected entity service
        """
        self.entity_service = entity_service
        logger.info("EntityManagementService initialized")

    async def get_entity(
        self, entity_model: str, entity_id: str, entity_version: str = ENTITY_VERSION
    ) -> Dict[str, Any]:
        """
        Retrieve a single entity by its technical ID.

        Args:
            entity_model: The type of entity
            entity_id: The technical UUID of the entity
            entity_version: The entity model version

        Returns:
            Dictionary containing entity data or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_id": entity_id,
                    "entity_model": entity_model,
                }

            result = await self.entity_service.get_by_id(
                entity_id, entity_model, entity_version
            )

            if not result:
                return {
                    "success": False,
                    "error": "Entity not found",
                    "entity_id": entity_id,
                    "entity_model": entity_model,
                }

            return {
                "success": True,
                "data": result.data,
                "metadata": {
                    "id": result.get_id(),
                    "state": result.metadata.state,
                    "entity_type": entity_model,
                },
            }

        except Exception as e:
            logger.exception("get_entity")
            return {
                "success": False,
                "error": str(e),
                "entity_id": entity_id,
                "entity_model": entity_model,
            }

    async def list_entities(
        self, entity_model: str, entity_version: str = ENTITY_VERSION
    ) -> Dict[str, Any]:
        """
        List all entities of a specific type.

        Args:
            entity_model: The type of entity to list
            entity_version: The entity model version

        Returns:
            Dictionary containing list of entities or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_model": entity_model,
                }

            results = await self.entity_service.find_all(entity_model, entity_version)

            entities = [
                {"id": r.get_id(), "data": r.data, "state": r.metadata.state}
                for r in results
            ]

            return {
                "success": True,
                "count": len(entities),
                "entities": entities,
                "entity_model": entity_model,
            }

        except Exception as e:
            logger.exception("list_entities")
            return {"success": False, "error": str(e), "entity_model": entity_model}

    async def create_entity(
        self,
        entity_model: str,
        entity_data: Dict[str, Any],
        entity_version: str = ENTITY_VERSION,
    ) -> Dict[str, Any]:
        """
        Create a new entity of a given model.

        Args:
            entity_model: The type of entity to create
            entity_data: The data for the new entity
            entity_version: The entity model version

        Returns:
            Dictionary containing created entity information or error
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_model": entity_model,
                }

            result = await self.entity_service.save(
                entity_data, entity_model, entity_version
            )

            return {
                "success": True,
                "entity_id": result.get_id(),
                "data": result.data,
                "entity_model": entity_model,
            }

        except Exception as e:
            logger.exception("create_entity")
            return {
                "success": False,
                "error": str(e),
                "entity_model": entity_model,
                "entity_data": entity_data,
            }

    async def update_entity(
        self,
        entity_model: str,
        entity_id: str,
        entity_data: Dict[str, Any],
        entity_version: str = ENTITY_VERSION,
    ) -> Dict[str, Any]:
        """
        Update an existing entity.

        Args:
            entity_model: The type of entity to update
            entity_id: The technical UUID of the entity
            entity_data: The updated data for the entity
            entity_version: The entity model version

        Returns:
            Dictionary containing updated entity information or error
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_model": entity_model,
                    "entity_id": entity_id,
                }

            result = await self.entity_service.update(
                entity_id, entity_data, entity_model, None, entity_version
            )

            return {
                "success": True,
                "entity_id": result.get_id(),
                "data": result.data,
                "entity_model": entity_model,
            }

        except Exception as e:
            logger.exception("update_entity")
            return {
                "success": False,
                "error": str(e),
                "entity_id": entity_id,
                "entity_model": entity_model,
            }

    async def delete_entity(
        self, entity_model: str, entity_id: str, entity_version: str = ENTITY_VERSION
    ) -> Dict[str, Any]:
        """
        Delete an entity by ID.

        Args:
            entity_model: The type of entity to delete
            entity_id: The technical UUID of the entity
            entity_version: The entity model version

        Returns:
            Dictionary containing deletion result or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_model": entity_model,
                    "entity_id": entity_id,
                }

            deleted_id = await self.entity_service.delete_by_id(
                entity_id, entity_model, entity_version
            )

            return {
                "success": True,
                "deleted_entity_id": deleted_id,
                "entity_model": entity_model,
            }

        except Exception as e:
            logger.exception("delete_entity")
            return {
                "success": False,
                "error": str(e),
                "entity_id": entity_id,
                "entity_model": entity_model,
            }

    async def search_entities(
        self,
        entity_model: str,
        search_conditions: Dict[str, Any],
        entity_version: str = ENTITY_VERSION,
    ) -> Dict[str, Any]:
        """
        Search entities with Cyoda-style search conditions.

        Args:
            entity_model: The type of entity to search
            search_conditions: Cyoda search condition structure or simple field-value pairs
            entity_version: The entity model version

        Returns:
            Dictionary containing search results or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_model": entity_model,
                }

            # Build search request from conditions
            builder = SearchConditionRequest.builder()

            # Check if this is a Cyoda-style search condition
            if (
                isinstance(search_conditions, dict)
                and search_conditions.get("type") == "group"
            ):
                # Handle complex Cyoda search structure (multiple conditions)
                operator = search_conditions.get("operator", "AND").upper()
                if operator == "AND":
                    builder.operator(LogicalOperator.AND)
                elif operator == "OR":
                    builder.operator(LogicalOperator.OR)

                conditions = search_conditions.get("conditions", [])
                for condition in conditions:
                    self._process_cyoda_condition(condition, builder)

            elif isinstance(search_conditions, dict) and search_conditions.get(
                "type"
            ) in ["simple", "lifecycle"]:
                # Handle single Cyoda condition (not wrapped in group)
                self._process_cyoda_condition(search_conditions, builder)

            else:
                # Handle simple field-value pairs (backward compatibility)
                for field, value in search_conditions.items():
                    builder.equals(field, value)

            search_request = builder.build()
            results = await self.entity_service.search(
                entity_model, search_request, entity_version
            )

            entities = [
                {"id": r.get_id(), "data": r.data, "state": r.metadata.state}
                for r in results
            ]

            return {
                "success": True,
                "count": len(entities),
                "entities": entities,
                "search_conditions": search_conditions,
                "entity_model": entity_model,
            }

        except Exception as e:
            logger.exception("search_entities")
            return {
                "success": False,
                "error": str(e),
                "search_conditions": search_conditions,
                "entity_model": entity_model,
            }

    def _process_cyoda_condition(self, condition: Dict[str, Any], builder: Any) -> None:
        """Process a single Cyoda condition and add it to the builder."""
        condition_type = condition.get("type")

        if condition_type == "lifecycle":
            # Handle lifecycle conditions (entity state)
            field = condition.get("field", "state")
            operator_type = condition.get("operatorType", "EQUALS")
            value = condition.get("value")

            # Map Cyoda operators to internal operators using enum mapping
            search_operator = CYODA_OPERATOR_MAPPING.get(
                operator_type, SearchOperator.EQUALS
            )
            builder.add_condition(field, search_operator, value)

        elif condition_type == "simple":
            # Handle simple JSON path conditions
            json_path = condition.get("jsonPath", "")
            operator_type = condition.get("operatorType", "EQUALS")
            value = condition.get("value")

            # Convert JSON path to field name (remove $. prefix)
            field = (
                json_path.replace("$.", "") if json_path.startswith("$.") else json_path
            )

            # Map Cyoda operators to internal operators using enum mapping
            search_operator = CYODA_OPERATOR_MAPPING.get(
                operator_type, SearchOperator.EQUALS
            )
            builder.add_condition(field, search_operator, value)
