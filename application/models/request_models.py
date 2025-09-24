"""
Request models for Purrfect Pets API.

Provides Pydantic models for request validation and documentation.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EntityIdParam(BaseModel):
    """Entity ID parameter model"""

    entity_id: str = Field(..., description="Entity ID")


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Success response model"""

    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")


class TransitionRequest(BaseModel):
    """Transition request model"""

    transition_name: str = Field(..., description="Name of the transition to execute")
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional transition parameters"
    )


class SearchRequest(BaseModel):
    """Search request model"""

    name: Optional[str] = Field(None, description="Search by name")
    category: Optional[str] = Field(None, description="Search by category")
    state: Optional[str] = Field(None, description="Search by state")


# Pet-specific models
class PetQueryParams(BaseModel):
    """Query parameters for pet listing"""

    status: Optional[str] = Field(None, description="Filter by pet status/state")
    category: Optional[str] = Field(None, description="Filter by pet category")
    breed: Optional[str] = Field(None, description="Filter by pet breed")
    min_price: Optional[float] = Field(
        None, alias="minPrice", description="Minimum price filter"
    )
    max_price: Optional[float] = Field(
        None, alias="maxPrice", description="Maximum price filter"
    )
    limit: int = Field(10, description="Number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class PetUpdateQueryParams(BaseModel):
    """Query parameters for pet updates"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


# Order-specific models
class OrderQueryParams(BaseModel):
    """Query parameters for order listing"""

    status: Optional[str] = Field(None, description="Filter by order status/state")
    userId: Optional[str] = Field(None, alias="userId", description="Filter by user ID")
    petId: Optional[str] = Field(None, alias="petId", description="Filter by pet ID")
    complete: Optional[bool] = Field(None, description="Filter by completion status")
    limit: int = Field(10, description="Number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class OrderUpdateQueryParams(BaseModel):
    """Query parameters for order updates"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


# User-specific models
class UserQueryParams(BaseModel):
    """Query parameters for user listing"""

    status: Optional[str] = Field(None, description="Filter by user status/state")
    emailVerified: Optional[bool] = Field(
        None, alias="emailVerified", description="Filter by email verification status"
    )
    limit: int = Field(10, description="Number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class UserUpdateQueryParams(BaseModel):
    """Query parameters for user updates"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )
    verification_token: Optional[str] = Field(
        None, description="Email verification token"
    )
