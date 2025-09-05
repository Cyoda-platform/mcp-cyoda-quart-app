"""
Search MCP Tools

This module provides FastMCP tools for search operations with full Cyoda compliance.
Contains only two tools: find_all and search.
"""

import os
import sys
from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.services import get_entity_service
from common.config.config import ENTITY_VERSION
from common.service.entity_service import SearchConditionRequest

# Create the MCP server for search operations
mcp = FastMCP("Search")


@mcp.tool
async def find_all(entity_model: str, entity_version: str = ENTITY_VERSION, ctx: Context = None) -> Dict[str, Any]:
    """
    Find all entities of a specific type using entity_service.find_all().

    Args:
        entity_model: The type of entity to retrieve (e.g., 'laureate', 'subscriber', 'job')
        entity_version: The entity model version (default: from config)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing all entities or error information
    """
    if ctx:
        await ctx.info(f"Finding all entities of type: {entity_model}")

    try:
        entity_service = get_entity_service()
        if not entity_service:
            return {
                "success": False,
                "error": "Entity service not available",
                "entity_model": entity_model
            }

        results = await entity_service.find_all(entity_model, entity_version)

        entities = [
            {
                "id": r.get_id(),
                "data": r.data,
                "state": r.metadata.state,
                "created_at": r.metadata.created_at,
                "updated_at": r.metadata.updated_at
            }
            for r in results
        ]

        return {
            "success": True,
            "count": len(entities),
            "entities": entities,
            "entity_model": entity_model,
            "entity_version": entity_version
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Error finding all entities: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "entity_model": entity_model
        }


@mcp.tool
async def search(
    entity_model: str,
    search_conditions: Dict[str, Any],
    entity_version: str = ENTITY_VERSION,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Search entities with Cyoda-native search conditions.

    Args:
        entity_model: The type of entity to search (e.g., 'laureate', 'subscriber', 'job')
        search_conditions: Cyoda search condition structure:
            {
                "type": "group",
                "operator": "AND" | "OR",
                "conditions": [
                    {
                        "type": "lifecycle",
                        "field": "state",
                        "operatorType": "EQUALS",
                        "value": "VALIDATED"
                    },
                    {
                        "type": "simple",
                        "jsonPath": "$.category",
                        "operatorType": "EQUALS" | "CONTAINS" | "GREATER_THAN" | "LESS_THAN",
                        "value": "physics"
                    }
                ]
            }

            For backward compatibility, simple field-value pairs are also supported:
            {"field1": "value1", "field2": "value2"}

        entity_version: The entity model version (default: from config)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing search results or error information
    """
    if ctx:
        await ctx.info(f"Searching {entity_model} entities with conditions: {search_conditions}")

    try:
        entity_service = get_entity_service()
        if not entity_service:
            return {
                "success": False,
                "error": "Entity service not available",
                "entity_model": entity_model
            }

        # Build search request from Cyoda conditions
        builder = SearchConditionRequest.builder()

        # Check if this is a Cyoda-style search condition
        if isinstance(search_conditions, dict) and search_conditions.get("type") == "group":
            # Handle complex Cyoda search structure (multiple conditions)
            operator = search_conditions.get("operator", "AND").lower()
            if operator == "and":
                builder.operator("and")
            elif operator == "or":
                builder.operator("or")

            conditions = search_conditions.get("conditions", [])
            for condition in conditions:
                _process_cyoda_condition(condition, builder)

        elif isinstance(search_conditions, dict) and search_conditions.get("type") in ["simple", "lifecycle"]:
            # Handle single Cyoda condition (not wrapped in group)
            _process_cyoda_condition(search_conditions, builder)

        else:
            # Handle simple field-value pairs (backward compatibility)
            for field, value in search_conditions.items():
                builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(entity_model, search_request, entity_version)

        entities = [
            {
                "id": r.get_id(),
                "data": r.data,
                "state": r.metadata.state,
                "created_at": r.metadata.created_at,
                "updated_at": r.metadata.updated_at
            }
            for r in results
        ]

        if ctx:
            await ctx.info(f"Found {len(entities)} {entity_model} entities matching conditions")

        return {
            "success": True,
            "count": len(entities),
            "entities": entities,
            "search_conditions": search_conditions,
            "entity_model": entity_model,
            "entity_version": entity_version
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Error searching entities: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "search_conditions": search_conditions,
            "entity_model": entity_model
        }


def _process_cyoda_condition(condition: Dict[str, Any], builder):
    """Process a single Cyoda condition and add it to the builder."""
    condition_type = condition.get("type")

    if condition_type == "lifecycle":
        # Handle lifecycle conditions (entity state)
        field = condition.get("field", "state")
        operator_type = condition.get("operatorType", "EQUALS")
        value = condition.get("value")

        # Map Cyoda operators to internal operators
        op_mapping = {
            "EQUALS": "eq",
            "NOT_EQUALS": "ne",
            "CONTAINS": "contains"
        }
        op = op_mapping.get(operator_type, "eq")
        builder.add_condition(field, op, value)

    elif condition_type == "simple":
        # Handle simple JSON path conditions
        json_path = condition.get("jsonPath", "")
        operator_type = condition.get("operatorType", "EQUALS")
        value = condition.get("value")

        # Convert JSON path to field name (remove $. prefix)
        field = json_path.replace("$.", "") if json_path.startswith("$.") else json_path

        # Map Cyoda operators to internal operators
        op_mapping = {
            "EQUALS": "eq",
            "IEQUALS": "ieq",  # Case-insensitive equals
            "NOT_EQUALS": "ne",
            "CONTAINS": "contains",
            "ICONTAINS": "icontains",  # Case-insensitive contains
            "GREATER_THAN": "gt",
            "LESS_THAN": "lt",
            "GREATER_THAN_OR_EQUAL": "gte",
            "LESS_THAN_OR_EQUAL": "lte",
            "STARTS_WITH": "startswith",
            "ENDS_WITH": "endswith",
            "IN": "in",
            "NOT_IN": "not_in"
        }
        op = op_mapping.get(operator_type, "eq")
        builder.add_condition(field, op, value)


# Export the MCP server
__all__ = ["mcp"]
