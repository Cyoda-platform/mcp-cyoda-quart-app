"""
Entity Management MCP Presentation Layer

This module provides FastMCP tools for entity management operations.
"""

import os
import sys
from typing import Dict, Any
from fastmcp import FastMCP, Context

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.services import get_entity_management_service
from common.config.config import ENTITY_VERSION

# Create the MCP server for entity management
mcp = FastMCP("Entity Management")


@mcp.tool
async def get_entity_tool(entity_model: str, entity_id: str, entity_version: str = ENTITY_VERSION, ctx: Context = None) -> Dict[str, Any]:
    """
    Retrieve a single entity by its technical ID.

    Args:
        entity_model: The type of entity (e.g., 'laureate', 'subscriber', 'job')
        entity_id: The technical UUID of the entity
        entity_version: The entity model version (default: from config)
        ctx: FastMCP context for logging

    Returns:
        The entity data or error information
    """
    if ctx:
        await ctx.info(f"Retrieving {entity_model}:{entity_id}")

    entity_management_service = get_entity_management_service()
    return await entity_management_service.get_entity(entity_model, entity_id, entity_version)


@mcp.tool
async def list_entities_tool(entity_model: str, entity_version: str = ENTITY_VERSION) -> Dict[str, Any]:
    """
    List all entities of a specific type.

    Args:
        entity_model: The type of entity to list
        entity_version: The entity model version

    Returns:
        List of entities or error information
    """
    entity_management_service = get_entity_management_service()
    return await entity_management_service.list_entities(entity_model, entity_version)


@mcp.tool
async def create_entity_tool(entity_model: str, entity_data: Dict[str, Any], entity_version: str = ENTITY_VERSION, ctx: Context = None) -> Dict[str, Any]:
    """
    Create a new entity of a given model.

    Args:
        entity_model: The type of entity to create
        entity_data: The data for the new entity
        entity_version: The entity model version
        ctx: FastMCP context for logging

    Returns:
        Created entity information or error
    """
    if ctx:
        await ctx.info(f"Creating {entity_model}")

    entity_management_service = get_entity_management_service()
    return await entity_management_service.create_entity(entity_model, entity_data, entity_version)


@mcp.tool
async def update_entity_tool(entity_model: str, entity_id: str, entity_data: Dict[str, Any], entity_version: str = ENTITY_VERSION, ctx: Context = None) -> Dict[str, Any]:
    """
    Update an existing entity.

    Args:
        entity_model: The type of entity to update
        entity_id: The technical UUID of the entity
        entity_data: The updated data for the entity
        entity_version: The entity model version
        ctx: FastMCP context for logging

    Returns:
        Updated entity information or error
    """
    if ctx:
        await ctx.info(f"Updating {entity_model}:{entity_id}")

    entity_management_service = get_entity_management_service()
    return await entity_management_service.update_entity(entity_model, entity_id, entity_data, entity_version)


@mcp.tool
async def delete_entity_tool(entity_model: str, entity_id: str, entity_version: str = ENTITY_VERSION, ctx: Context = None) -> Dict[str, Any]:
    """
    Delete an entity by ID.

    Args:
        entity_model: The type of entity to delete
        entity_id: The technical UUID of the entity
        entity_version: The entity model version
        ctx: FastMCP context for logging

    Returns:
        Deletion result or error information
    """
    if ctx:
        await ctx.info(f"Deleting {entity_model}:{entity_id}")

    entity_management_service = get_entity_management_service()
    return await entity_management_service.delete_entity(entity_model, entity_id, entity_version)