"""
Response models for Application API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Success status")
    error: Dict[str, Any] = Field(..., description="Error details")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = Field(False, description="Success status")
    error: Dict[str, Any] = Field(..., description="Validation error details")


class DeleteResponse(BaseModel):
    """Delete operation response"""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")


class HnItemResponse(BaseModel):
    """Response model for single HN item"""
    success: bool = Field(True, description="Success status")
    data: Dict[str, Any] = Field(..., description="HN item data")
    message: Optional[str] = Field(None, description="Optional message")


class PaginationInfo(BaseModel):
    """Pagination information"""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Items skipped")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class HnItemListResponse(BaseModel):
    """Response model for list of HN items"""
    success: bool = Field(True, description="Success status")
    data: Dict[str, Any] = Field(..., description="Items and pagination data")


class BulkCreateItemResult(BaseModel):
    """Result for individual item in bulk create"""
    technical_id: Optional[str] = Field(None, description="Technical ID if created")
    id: int = Field(..., description="HN item ID")
    status: str = Field(..., description="Creation status")
    error: Optional[str] = Field(None, description="Error message if failed")


class BulkCreateSummary(BaseModel):
    """Summary of bulk create operation"""
    total_requested: int = Field(..., description="Total items requested")
    successfully_created: int = Field(..., description="Successfully created items")
    failed: int = Field(..., description="Failed items")


class BulkCreateResponse(BaseModel):
    """Response model for bulk create operation"""
    success: bool = Field(True, description="Success status")
    data: Dict[str, Any] = Field(..., description="Bulk create results")
    message: str = Field(..., description="Operation message")


class TransitionResponse(BaseModel):
    """Response model for workflow transition"""
    success: bool = Field(True, description="Success status")
    data: Dict[str, Any] = Field(..., description="Transition details")
    message: str = Field(..., description="Transition message")


class HierarchyStats(BaseModel):
    """Hierarchy statistics"""
    total_parents: int = Field(..., description="Total parent items")
    total_children: int = Field(..., description="Total child items")
    max_depth: int = Field(..., description="Maximum hierarchy depth")


class HierarchyResponse(BaseModel):
    """Response model for item hierarchy"""
    success: bool = Field(True, description="Success status")
    data: Dict[str, Any] = Field(..., description="Hierarchy data")
