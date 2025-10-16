"""
Response models for Task API endpoints.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """Response model for single task operations."""

    # This will contain the actual task data
    # The structure will match the Task entity fields
    pass  # Will be populated with actual task data


class TaskListResponse(BaseModel):
    """Response model for task list operations."""

    entities: List[Dict[str, Any]] = Field(description="List of task entities")
    total: int = Field(description="Total number of tasks")


class TaskSearchResponse(BaseModel):
    """Response model for task search operations."""

    entities: List[Dict[str, Any]] = Field(description="List of matching task entities")
    total: int = Field(description="Total number of matching tasks")
