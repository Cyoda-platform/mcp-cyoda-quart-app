"""
Workflow Management MCP Presentation Layer

This module provides FastMCP tools for workflow management operations.
"""

import os
import sys
from typing import Dict, Any, List
from fastmcp import FastMCP, Context

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.services import get_workflow_management_service

# Create the MCP server for workflow management operations
mcp = FastMCP("Workflow Management")


@mcp.tool
async def export_entity_workflows_tool(
    entity_name: str,
    model_version: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Export entity workflows.
    
    Args:
        entity_name: Name of the entity
        model_version: Version of the model
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing exported workflows or error information
    """
    if ctx:
        await ctx.info(f"Exporting workflows for entity {entity_name} version {model_version}")
    
    workflow_management_service = get_workflow_management_service()
    return await workflow_management_service.export_entity_workflows(
        entity_name=entity_name,
        model_version=model_version
    )


@mcp.tool
async def import_entity_workflows_tool(
    entity_name: str,
    model_version: str,
    workflows: List[Dict[str, Any]],
    import_mode: str = "REPLACE",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Import entity workflows.
    
    Args:
        entity_name: Name of the entity
        model_version: Version of the model
        workflows: List of workflow definitions
        import_mode: Import mode ("REPLACE" or other supported modes)
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing import result or error information
    """
    if ctx:
        await ctx.info(f"Importing {len(workflows)} workflows for entity {entity_name} version {model_version}")
    
    workflow_management_service = get_workflow_management_service()
    return await workflow_management_service.import_entity_workflows(
        entity_name=entity_name,
        model_version=model_version,
        workflows=workflows,
        import_mode=import_mode
    )


@mcp.tool
async def copy_workflows_between_entities_tool(
    source_entity_name: str,
    source_model_version: str,
    target_entity_name: str,
    target_model_version: str,
    import_mode: str = "REPLACE",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Copy workflows from one entity to another.
    
    Args:
        source_entity_name: Name of the source entity
        source_model_version: Version of the source model
        target_entity_name: Name of the target entity
        target_model_version: Version of the target model
        import_mode: Import mode ("REPLACE" or other supported modes)
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing copy result or error information
    """
    if ctx:
        await ctx.info(f"Copying workflows from {source_entity_name} v{source_model_version} to {target_entity_name} v{target_model_version}")
    
    workflow_management_service = get_workflow_management_service()
    return await workflow_management_service.copy_workflows_between_entities(
        source_entity_name=source_entity_name,
        source_model_version=source_model_version,
        target_entity_name=target_entity_name,
        target_model_version=target_model_version,
        import_mode=import_mode
    )