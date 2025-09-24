"""
Response models for Purrfect Pets API.

Provides Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response model"""

    error: str = Field(..., description="Validation error message")
    code: str = Field("VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Validation error details"
    )


class DeleteResponse(BaseModel):
    """Delete operation response model"""

    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Entity existence check response model"""

    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., description="Entity ID that was checked")


class CountResponse(BaseModel):
    """Entity count response model"""

    count: int = Field(..., description="Number of entities", ge=0)


class TransitionResponse(BaseModel):
    """Transition execution response model"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previousState: Optional[str] = Field(None, description="Previous entity state")
    newState: str = Field(..., description="New entity state")


class TransitionsResponse(BaseModel):
    """Available transitions response model"""

    entity_id: str = Field(..., description="Entity ID")
    current_state: Optional[str] = Field(None, description="Current entity state")
    available_transitions: List[str] = Field(
        ..., description="List of available transitions"
    )


# Pet-specific response models
class PetResponse(BaseModel):
    """Single pet response model"""

    id: str = Field(..., description="Pet ID")
    name: str = Field(..., description="Pet name")
    category: Optional[Dict[str, Any]] = Field(None, description="Pet category")
    photoUrls: List[str] = Field(..., description="Pet photo URLs")
    tags: Optional[List[Dict[str, Any]]] = Field(None, description="Pet tags")
    breed: Optional[str] = Field(None, description="Pet breed")
    age: Optional[int] = Field(None, description="Pet age in months")
    price: Optional[float] = Field(None, description="Pet price")
    state: str = Field(..., description="Pet state")


class PetListResponse(BaseModel):
    """Pet list response model"""

    pets: List[Dict[str, Any]] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets", ge=0)
    limit: int = Field(..., description="Results limit", ge=1)
    offset: int = Field(..., description="Results offset", ge=0)


class PetSearchResponse(BaseModel):
    """Pet search response model"""

    pets: List[Dict[str, Any]] = Field(..., description="List of matching pets")
    total: int = Field(..., description="Total number of matching pets", ge=0)


# Order-specific response models
class OrderResponse(BaseModel):
    """Single order response model"""

    id: str = Field(..., description="Order ID")
    petId: str = Field(..., description="Pet ID")
    userId: str = Field(..., description="User ID")
    quantity: int = Field(..., description="Order quantity")
    totalAmount: Optional[float] = Field(None, description="Total order amount")
    complete: bool = Field(..., description="Order completion status")
    state: str = Field(..., description="Order state")


class OrderListResponse(BaseModel):
    """Order list response model"""

    orders: List[Dict[str, Any]] = Field(..., description="List of orders")
    total: int = Field(..., description="Total number of orders", ge=0)
    limit: int = Field(..., description="Results limit", ge=1)
    offset: int = Field(..., description="Results offset", ge=0)


class OrderSearchResponse(BaseModel):
    """Order search response model"""

    orders: List[Dict[str, Any]] = Field(..., description="List of matching orders")
    total: int = Field(..., description="Total number of matching orders", ge=0)


# User-specific response models
class UserResponse(BaseModel):
    """Single user response model"""

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    emailVerified: bool = Field(..., description="Email verification status")
    state: str = Field(..., description="User state")


class UserListResponse(BaseModel):
    """User list response model"""

    users: List[Dict[str, Any]] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users", ge=0)
    limit: int = Field(..., description="Results limit", ge=1)
    offset: int = Field(..., description="Results offset", ge=0)


class UserSearchResponse(BaseModel):
    """User search response model"""

    users: List[Dict[str, Any]] = Field(..., description="List of matching users")
    total: int = Field(..., description="Total number of matching users", ge=0)
