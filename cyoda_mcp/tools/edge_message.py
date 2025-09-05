"""
Edge Message MCP Presentation Layer

This module provides FastMCP tools for edge message operations.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP, Context

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from service.services import get_edge_message_service

# Create the MCP server for edge message operations
mcp = FastMCP("Edge Message")


@mcp.tool
async def get_edge_message_tool(message_id: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Retrieve an edge message by ID.
    
    Args:
        message_id: The ID of the message to retrieve
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing message data or error information
    """
    if ctx:
        await ctx.info(f"Retrieving edge message: {message_id}")
    
    edge_message_service = get_edge_message_service()
    return await edge_message_service.get_message_by_id(message_id)


@mcp.tool
async def send_edge_message_tool(
    subject: str,
    content: Dict[str, Any],
    message_id: Optional[str] = None,
    user_id: Optional[str] = None,
    recipient: Optional[str] = None,
    reply_to: Optional[str] = None,
    correlation_id: Optional[str] = None,
    content_encoding: Optional[str] = None,
    content_length: Optional[int] = None,
    content_type: str = "application/json",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Send a new edge message.
    
    Args:
        subject: Message subject
        content: Message content as dictionary
        message_id: Optional message ID
        user_id: Optional user ID
        recipient: Optional recipient
        reply_to: Optional reply-to address
        correlation_id: Optional correlation ID
        content_encoding: Optional content encoding
        content_length: Optional content length
        content_type: Content type (default: application/json)
        ctx: FastMCP context for logging
    
    Returns:
        Dictionary containing send result or error information
    """
    if ctx:
        await ctx.info(f"Sending edge message with subject: {subject}")
    
    edge_message_service = get_edge_message_service()
    return await edge_message_service.send_message(
        subject=subject,
        content=content,
        message_id=message_id,
        user_id=user_id,
        recipient=recipient,
        reply_to=reply_to,
        correlation_id=correlation_id,
        content_encoding=content_encoding,
        content_length=content_length,
        content_type=content_type
    )
