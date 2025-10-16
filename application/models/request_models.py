"""
Request models for Task API endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TaskQueryParams(BaseModel):
    """Query parameters for listing tasks."""
    
    priority: Optional[str] = Field(
        default=None,
        description="Filter by priority (LOW, MEDIUM, HIGH, URGENT)"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Filter by assignee"
    )
    state: Optional[str] = Field(
        default=None,
        description="Filter by workflow state"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of items to return"
    )


class TaskUpdateQueryParams(BaseModel):
    """Query parameters for updating tasks."""
    
    transition: Optional[str] = Field(
        default=None,
        description="Optional workflow transition to trigger"
    )
