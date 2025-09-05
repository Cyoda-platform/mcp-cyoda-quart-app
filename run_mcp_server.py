#!/usr/bin/env python3
"""
Standalone MCP Server Runner

This script runs the Cyoda MCP server independently from the main Quart application.
It initializes all necessary services with dependency injection and starts the MCP server.
"""

import asyncio
import logging
import sys
import os
import argparse

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_mcp_server_standalone(port=None):
    """Run the MCP server in standalone mode with full service initialization."""
    try:
        # Import and initialize the MCP server
        from cyoda_mcp.server import mcp_server, _services_initialized

        if not _services_initialized:
            logger.error("Failed to initialize services. Check your environment configuration.")
            return 1

        logger.info("Starting Cyoda MCP Server in standalone mode...")
        logger.info(f"Server name: {mcp_server.name}")

        # Get available tools
        tools = await mcp_server.get_tools()
        logger.info(f"Available tools: {len(tools)}")
        for tool in tools:
            if hasattr(tool, 'name'):
                logger.info(f"  - {tool.name}: {getattr(tool, 'description', 'No description')}")
            else:
                logger.info(f"  - {tool}")  # Fallback for string tools

        if port:
            # Run HTTP server on specified port
            logger.info(f"Starting MCP server on HTTP port {port}")
            logger.info(f"Server will be available at http://localhost:{port}")

            # Use FastMCP's built-in HTTP server
            await mcp_server.run_http(port=port)
        else:
            # For stdio mode, we just need to keep the server alive
            logger.info("MCP server is ready and initialized")
            logger.info("All tools are available and services are running")
            logger.info("Use this server with an MCP client via stdio transport")

            # Keep the server alive
            import signal

            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                logger.info("Received shutdown signal, stopping server...")
                raise KeyboardInterrupt()

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Server shutdown requested")
                return 0

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Cyoda MCP Server')
    parser.add_argument('--port', type=int, help='HTTP port to run server on (default: stdio mode)')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    args = parser.parse_args()

    logger.info("Cyoda MCP Server - Standalone Mode")
    logger.info("=" * 50)

    if args.port:
        logger.info(f"Running in HTTP mode on {args.host}:{args.port}")
    else:
        logger.info("Running in stdio mode")

    # Check environment variables
    required_vars = ['CYODA_CLIENT_ID', 'CYODA_CLIENT_SECRET', 'CYODA_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work correctly")
    else:
        logger.info("All required environment variables are set")

    # Run the server
    try:
        exit_code = asyncio.run(run_mcp_server_standalone(port=args.port))
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
