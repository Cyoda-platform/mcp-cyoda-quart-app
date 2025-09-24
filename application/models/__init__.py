"""
Models package for Purrfect Pets Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    EntityIdParam,
    ErrorResponse,
    PetQueryParams,
    PetUpdateQueryParams,
    OrderQueryParams,
    OrderUpdateQueryParams,
    UserQueryParams,
    UserUpdateQueryParams,
    SearchRequest,
    SuccessResponse,
    TransitionRequest,
)
from .response_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse as ResponseErrorResponse,
    ExistsResponse,
    PetListResponse,
    PetResponse,
    PetSearchResponse,
    OrderListResponse,
    OrderResponse,
    OrderSearchResponse,
    UserListResponse,
    UserResponse,
    UserSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "EntityIdParam",
    "ErrorResponse",
    "PetQueryParams",
    "PetUpdateQueryParams",
    "OrderQueryParams",
    "OrderUpdateQueryParams",
    "UserQueryParams",
    "UserUpdateQueryParams",
    "SearchRequest",
    "SuccessResponse",
    "TransitionRequest",
    # Response models
    "CountResponse",
    "DeleteResponse",
    "ExistsResponse",
    "ResponseErrorResponse",
    "PetListResponse",
    "PetResponse",
    "PetSearchResponse",
    "OrderListResponse",
    "OrderResponse",
    "OrderSearchResponse",
    "UserListResponse",
    "UserResponse",
    "UserSearchResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
