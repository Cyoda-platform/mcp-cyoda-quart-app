"""
Models package for Purrfect Pets Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    EntityIdParam,
    ErrorResponse,
    OrderQueryParams,
    OrderUpdateQueryParams,
    PetQueryParams,
    PetUpdateQueryParams,
    SearchRequest,
    SuccessResponse,
    TransitionRequest,
    UserQueryParams,
    UserUpdateQueryParams,
)
from .response_models import (
    CountResponse,
    DeleteResponse,
)
from .response_models import ErrorResponse as ResponseErrorResponse
from .response_models import (
    ExistsResponse,
    OrderListResponse,
    OrderResponse,
    OrderSearchResponse,
    PetListResponse,
    PetResponse,
    PetSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    UserListResponse,
    UserResponse,
    UserSearchResponse,
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
