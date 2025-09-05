"""
Main MCP Server for Cyoda Integration

This module provides a unified FastMCP server that composes all category servers
with proper prefixes for organized tool catalogs.
"""

import os
import sys
import asyncio
import logging
from fastmcp import FastMCP

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import presentation-only category servers
from cyoda_mcp.tools.entity_management import mcp as mcp_entity
from cyoda_mcp.tools.search import mcp as mcp_search
from cyoda_mcp.tools.edge_message import mcp as mcp_edge_message
from cyoda_mcp.tools.workflow_management import mcp as mcp_workflow_management
from cyoda_mcp.tools.deployment import mcp as mcp_deployment

logger = logging.getLogger(__name__)

# Initialize services with dependency injection when MCP server starts
def initialize_mcp_services():
    """Initialize all services with proper dependency injection configuration."""
    from service.config import get_service_config, validate_configuration
    from service.services import initialize_services

    try:
        # Validate configuration first
        validation = validate_configuration()
        if not validation['valid']:
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
_services_initialized = initialize_mcp_services()

# Single, unified server
main = FastMCP("Cyoda Client Tools 🚀")


async def setup():
    """Setup the main server by importing all category servers with prefixes."""
    try:
        # Namespace each category to keep the catalog tidy
        await main.import_server(mcp_entity, prefix="entity")
        await main.import_server(mcp_search, prefix="search")
        await main.import_server(mcp_edge_message, prefix="edge_message")
        await main.import_server(mcp_workflow_management, prefix="workflow_mgmt")
        await main.import_server(mcp_deployment, prefix="deployment")

        logger.info("All MCP category servers imported successfully")
    except Exception as e:
        logger.error(f"Failed to setup MCP servers: {e}")
        raise


def set_integrated_mode():
    """Set the server to integrated mode (not standalone)."""
    # Services are already initialized, nothing to do
    pass


def get_mcp() -> FastMCP:
    """
    Get the configured FastMCP server instance.
    
    Returns:
        The FastMCP server instance
    """
    return main


def run_mcp(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8002):
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


def start(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8002):
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
    MCP_TRANSPORT = os.getenv('MCP_TRANSPORT')
    if MCP_TRANSPORT == "http":
        run_mcp(transport="http", host="0.0.0.0", port=8002)
    elif MCP_TRANSPORT == "sse":
        run_mcp(transport="sse", host="0.0.0.0", port=8002)
    else:
        run_mcp(transport="stdio")
