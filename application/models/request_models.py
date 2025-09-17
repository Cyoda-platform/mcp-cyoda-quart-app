"""
Request models for Application API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HnItemQueryParams(BaseModel):
    """Query parameters for listing HN items"""
    type: Optional[str] = Field(None, description="Filter by item type")
    by: Optional[str] = Field(None, description="Filter by author username")
    source: Optional[str] = Field(None, description="Filter by source")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    limit: int = Field(50, ge=1, le=200, description="Number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    sort: str = Field("time", description="Sort field")
    order: str = Field("desc", description="Sort order")


class HnItemUpdateQueryParams(BaseModel):
    """Query parameters for updating HN items"""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class BulkCreateRequest(BaseModel):
    """Request model for bulk creating HN items"""
    items: List[Dict[str, Any]] = Field(..., description="List of HN items to create")
    auto_validate: bool = Field(False, description="Automatically trigger validation")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""
    transition: str = Field(..., description="Transition name to trigger")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class HierarchyQueryParams(BaseModel):
    """Query parameters for getting item hierarchy"""
    include_parents: bool = Field(True, description="Include parent items")
    include_children: bool = Field(True, description="Include child items")
    max_depth: int = Field(5, ge=1, le=10, description="Maximum depth for hierarchy")
