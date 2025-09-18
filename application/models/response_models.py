"""
Response models for Application API endpoints.

Provides Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response model"""
    error: str = Field(..., description="Validation error message")
    code: str = Field("VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Validation error details")


class DeleteResponse(BaseModel):
    """Standard delete response model"""
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Delete confirmation message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Entity existence check response model"""
    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., alias="entityId", description="Entity ID that was checked")


class CountResponse(BaseModel):
    """Entity count response model"""
    count: int = Field(..., description="Number of entities")


class TransitionResponse(BaseModel):
    """Workflow transition response model"""
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Transition result message")
    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    previous_state: Optional[str] = Field(None, alias="previousState", description="Previous workflow state")
    new_state: Optional[str] = Field(None, alias="newState", description="New workflow state")


class TransitionsResponse(BaseModel):
    """Available transitions response model"""
    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    current_state: Optional[str] = Field(None, alias="currentState", description="Current workflow state")
    available_transitions: List[str] = Field(..., alias="availableTransitions", description="Available transitions")


# Pet-specific response models
class PetResponse(BaseModel):
    """Single Pet response model"""
    data: Dict[str, Any] = Field(..., description="Pet data")


class PetListResponse(BaseModel):
    """Pet list response model"""
    entities: List[Dict[str, Any]] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets")


class PetSearchResponse(BaseModel):
    """Pet search response model"""
    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


# Category-specific response models
class CategoryResponse(BaseModel):
    """Single Category response model"""
    data: Dict[str, Any] = Field(..., description="Category data")


class CategoryListResponse(BaseModel):
    """Category list response model"""
    entities: List[Dict[str, Any]] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")


class CategorySearchResponse(BaseModel):
    """Category search response model"""
    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


# Order-specific response models
class OrderResponse(BaseModel):
    """Single Order response model"""
    data: Dict[str, Any] = Field(..., description="Order data")


class OrderListResponse(BaseModel):
    """Order list response model"""
    entities: List[Dict[str, Any]] = Field(..., description="List of orders")
    total: int = Field(..., description="Total number of orders")


class OrderSearchResponse(BaseModel):
    """Order search response model"""
    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


# User-specific response models
class UserResponse(BaseModel):
    """Single User response model"""
    data: Dict[str, Any] = Field(..., description="User data")


class UserListResponse(BaseModel):
    """User list response model"""
    entities: List[Dict[str, Any]] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


class UserSearchResponse(BaseModel):
    """User search response model"""
    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
