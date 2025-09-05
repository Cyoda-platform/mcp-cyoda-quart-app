"""
Deployment MCP Presentation Layer

This module provides FastMCP tools for deployment operations.
"""

import os
import sys
from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.services import get_deployment_service

# Create the MCP server for deployment operations
mcp = FastMCP("Deployment")


@mcp.tool
async def schedule_deploy_env_tool(
        technical_id: str,
) -> Dict[str, Any]:
    """
    Schedule environment deployment.
    
    Args:
        technical_id: Technical ID of the environment

    Returns:
        Dictionary containing deployment result or error information
    """

    deployment_service = get_deployment_service()
    return await deployment_service.schedule_deploy_env(
        technical_id=technical_id,
    )


@mcp.tool
async def schedule_build_user_application_tool(
        technical_id: str
) -> Dict[str, Any]:
    """
    Schedule user application build.
    
    Args:
        technical_id: Technical ID of the application
        user_id: User ID initiating the build
        entity_data: Entity data for build
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing build result or error information
    """
    deployment_service = get_deployment_service()
    return await deployment_service.schedule_build_user_application(
        technical_id=technical_id
    )


@mcp.tool
async def schedule_deploy_user_application_tool(
        technical_id: str
) -> Dict[str, Any]:
    """
    Schedule user application deployment.
    
    Args:
        technical_id: Technical ID of the application
        user_id: User ID initiating the deployment
        entity_data: Entity data for deployment
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing deployment result or error information
    """
    deployment_service = get_deployment_service()
    return await deployment_service.schedule_deploy_user_application(
        technical_id=technical_id
    )


@mcp.tool
async def get_env_deploy_status_tool(
        build_id: str) -> Dict[str, Any]:
    """
    Get deployment status for a specific build.
    
    Args:
        build_id: Build ID to check status for
        user_id: Optional user ID
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing deployment status or error information
    """

    deployment_service = get_deployment_service()
    return await deployment_service.get_env_deploy_status(
        build_id=build_id)
