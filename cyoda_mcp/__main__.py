#!/usr/bin/env python3
"""
Console entrypoint for `mcp-cyoda-client`.
Keep this minimal so users get a reliable one-liner.
"""

import sys
import os
import argparse
import logging
import asyncio
from typing import Optional

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate required environment variables.

    Returns:
        Tuple of (is_valid, missing_variables)
    """
    required_vars = ['CYODA_CLIENT_ID', 'CYODA_CLIENT_SECRET', 'CYODA_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    return len(missing_vars) == 0, missing_vars

def print_version() -> None:
    """Print version information."""
    try:
        from importlib.metadata import version
        pkg_version = version("mcp-cyoda-client")
        print(f"mcp-cyoda-client version {pkg_version}")
    except Exception:
        print("mcp-cyoda-client (version unknown)")

def start_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8002) -> int:
    """
    Start the Cyoda MCP server.

    Args:
        transport: Transport type ("stdio", "http", "sse")
        host: Host to bind to (for HTTP/SSE transport)
        port: Port to bind to (for HTTP/SSE transport)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger = logging.getLogger(__name__)

    try:
        # Import lazily so import errors show nice messages for missing deps
        from .server import start, _services_initialized

        if not _services_initialized:
            logger.error("Failed to initialize Cyoda services. Check your environment configuration.")
            logger.error("Required environment variables: CYODA_CLIENT_ID, CYODA_CLIENT_SECRET, CYODA_HOST")
            return 1

        # Start the server (this will setup and run)
        logger.info(f"Starting Cyoda MCP server with {transport} transport...")
        if transport == "stdio":
            logger.info("Server ready for MCP client connections via stdio")
        else:
            logger.info(f"Server will be available at {transport}://{host}:{port}")

        # Run the server (this will block)
        start(transport=transport, host=host, port=port)
        return 0

    except ImportError as e:
        print(f"Failed to import server components: {e}", file=sys.stderr)
        print("Is the package installed correctly?", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Failed to start Cyoda MCP server: {e}")
        return 1

def main() -> None:
    """
    Console entrypoint for `mcp-cyoda-client`.
    """
    parser = argparse.ArgumentParser(
        description='Cyoda MCP Server - Model Context Protocol integration for Cyoda platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-cyoda-client                    # Start with stdio transport (default)
  mcp-cyoda-client --transport http   # Start with HTTP transport
  mcp-cyoda-client --transport sse    # Start with SSE transport
  mcp-cyoda-client --port 9000        # Use custom port
  mcp-cyoda-client --version          # Show version information

Environment Variables:
  CYODA_CLIENT_ID      - Cyoda client ID (required)
  CYODA_CLIENT_SECRET  - Cyoda client secret (required)
  CYODA_HOST           - Cyoda host (e.g., client-123.eu.cyoda.net) (required)
  MCP_TRANSPORT        - Default transport if not specified via --transport
        """
    )
    
    parser.add_argument(
        '--transport', 
        choices=['stdio', 'http', 'sse'],
        help='Transport type (default: stdio, or from MCP_TRANSPORT env var)'
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to for HTTP/SSE transport (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8002,
        help='Port to bind to for HTTP/SSE transport (default: 8002)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print_version()
        return
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Determine transport
    transport = args.transport or os.getenv('MCP_TRANSPORT', 'stdio')
    
    # Validate environment
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these environment variables before running the server")
        sys.exit(1)
    
    logger.info("Cyoda MCP Server - Starting...")
    logger.info("=" * 50)
    logger.info(f"Transport: {transport}")
    if transport in ['http', 'sse']:
        logger.info(f"Host: {args.host}")
        logger.info(f"Port: {args.port}")
    
    # Start the server
    try:
        exit_code = start_server(
            transport=transport,
            host=args.host,
            port=args.port
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
