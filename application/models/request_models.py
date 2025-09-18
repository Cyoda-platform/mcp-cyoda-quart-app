"""
Request models for Application API endpoints.

Provides Pydantic models for request validation and documentation.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EntityIdParam(BaseModel):
    """Entity ID parameter model"""
    entity_id: str = Field(..., description="Entity identifier")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool = Field(True, description="Success indicator")
    message: Optional[str] = Field(None, description="Success message")


class TransitionRequest(BaseModel):
    """Request model for workflow transitions"""
    transition_name: str = Field(..., alias="transitionName", description="Name of the transition to execute")


class SearchRequest(BaseModel):
    """Generic search request model"""
    criteria: Dict[str, Any] = Field(..., description="Search criteria")


# Pet-specific models
class PetQueryParams(BaseModel):
    """Query parameters for Pet listing endpoints"""
    status: Optional[str] = Field(None, description="Filter by pet status")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[str] = Field(None, description="Filter by tags (comma-separated)")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class PetUpdateQueryParams(BaseModel):
    """Query parameters for Pet update endpoints"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


# Category-specific models
class CategoryQueryParams(BaseModel):
    """Query parameters for Category listing endpoints"""
    state: Optional[str] = Field(None, description="Filter by category state")
    name: Optional[str] = Field(None, description="Filter by category name")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class CategoryUpdateQueryParams(BaseModel):
    """Query parameters for Category update endpoints"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


# Order-specific models
class OrderQueryParams(BaseModel):
    """Query parameters for Order listing endpoints"""
    status: Optional[str] = Field(None, description="Filter by order status")
    user_id: Optional[str] = Field(None, alias="userId", description="Filter by user ID")
    pet_id: Optional[str] = Field(None, alias="petId", description="Filter by pet ID")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class OrderUpdateQueryParams(BaseModel):
    """Query parameters for Order update endpoints"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


# User-specific models
class UserQueryParams(BaseModel):
    """Query parameters for User listing endpoints"""
    status: Optional[str] = Field(None, description="Filter by user status")
    email: Optional[str] = Field(None, description="Filter by email")
    username: Optional[str] = Field(None, description="Filter by username")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class UserUpdateQueryParams(BaseModel):
    """Query parameters for User update endpoints"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")
