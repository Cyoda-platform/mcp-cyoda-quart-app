# cyoda_mcp/server.py
from __future__ import annotations

"""
Main MCP Server for Cyoda Integration

This module provides a unified FastMCP server that composes all category servers
with proper prefixes for organized tool catalogs.
"""

import asyncio
import logging
import os
import sys
from typing import Literal

from fastmcp import FastMCP

from cyoda_mcp.tools.edge_message import mcp as mcp_edge_message
from cyoda_mcp.tools.entity_management import mcp as mcp_entity
from cyoda_mcp.tools.search import mcp as mcp_search
from cyoda_mcp.tools.workflow_management import mcp as mcp_workflow_management

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


def initialize_mcp_services() -> bool:
    """Initialize all services with proper dependency injection configuration.

    Returns:
        bool: True if services initialized successfully, False otherwise.
    """
    from services.config import get_service_config, validate_configuration
    from services.services import initialize_services

    try:
        # Validate configuration first
        validation = validate_configuration()
        if not validation["valid"]:
            logger.error("MCP service configuration validation failed!")
            return False

        # Use centralized configuration
        config = get_service_config()
        logger.info("Initializing MCP services at startup...")
        initialize_services(config)
        logger.info("MCP services initialized successfully with dependency injection")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MCP services: {e}")
        return False


# Initialize services when the module is loaded
_services_initialized: bool = initialize_mcp_services()

# Single, unified server
main: FastMCP = FastMCP("Cyoda Client Tools 🚀")


async def setup() -> None:
    """Setup the main server by importing all category servers with prefixes."""
    try:
        # Namespace each category to keep the catalog tidy
        await main.import_server(mcp_entity, prefix="entity")
        await main.import_server(mcp_search, prefix="search")
        await main.import_server(mcp_edge_message, prefix="edge_message")
        await main.import_server(mcp_workflow_management, prefix="workflow_mgmt")

        logger.info("All MCP category servers imported successfully")
    except Exception as e:
        logger.error(f"Failed to setup MCP servers: {e}")
        raise


def set_integrated_mode() -> None:
    """Set the server to integrated mode (not standalone)."""
    # Services are already initialized, nothing to do
    return None


def get_mcp() -> FastMCP:
    """
    Get the configured FastMCP server instance.

    Returns:
        FastMCP: The FastMCP server instance.
    """
    return main


def run_mcp(
    transport: Literal["stdio", "http", "sse"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8002,
) -> None:
    """
    Run the FastMCP server (synchronous).

    Args:
        transport: Transport type ("stdio", "http", "sse")
        host: Host to bind to (for HTTP/SSE transport)
        port: Port to bind to (for HTTP/SSE transport)
    """
    if transport == "stdio":
        logger.info("Starting FastMCP server with STDIO transport")
        main.run()
    elif transport == "http":
        logger.info(f"Starting FastMCP server with HTTP transport on {host}:{port}")
        main.run(transport="http", host=host, port=port)
    elif transport == "sse":
        logger.info(f"Starting FastMCP server with SSE transport on {host}:{port}")
        main.run(transport="sse", host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


def start(
    transport: Literal["stdio", "http", "sse"] = "stdio",
    host: str = "127.0.0.1",
    port: int = 8002,
) -> None:
    """
    Boot the MCP server with the specified transport.
    Read any API keys from env vars.
    Don't require users to edit this file.

    This is the main entry point for the packaged CLI.

    Args:
        transport: Transport type ("stdio", "http", "sse")
        host: Host to bind to (for HTTP/SSE transport)
        port: Port to bind to (for HTTP/SSE transport)
    """
    # Setup the server composition first
    asyncio.run(setup())

    # Then run the server
    run_mcp(transport=transport, host=host, port=port)


if __name__ == "__main__":
    # Setup the server composition
    asyncio.run(setup())

    # Run the MCP server standalone
    MCP_TRANSPORT = os.getenv("MCP_TRANSPORT")
    mcp_host = os.getenv("MCP_HOST", "127.0.0.1")  # Default to localhost for security
    mcp_port = int(os.getenv("MCP_PORT", "8002"))

    if MCP_TRANSPORT == "http":
        run_mcp(transport="http", host=mcp_host, port=mcp_port)
    elif MCP_TRANSPORT == "sse":
        run_mcp(transport="sse", host=mcp_host, port=mcp_port)
    else:
        run_mcp(transport="stdio")
