"""
Models package for Pet Application.

Provides request and response models for comprehensive Pet API validation.
"""

from .request_models import (
    ErrorResponse,
    PetQueryParams,
    PetUpdateQueryParams,
    SearchRequest,
    SuccessResponse,
    TransitionRequest,
)
from .response_models import (
    CountResponse,
    DeleteResponse,
    ExistsResponse,
    PetListResponse,
    PetResponse,
    PetSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "ErrorResponse",
    "PetQueryParams",
    "PetUpdateQueryParams",
    "SearchRequest",
    "SuccessResponse",
    "TransitionRequest",
    # Response models
    "CountResponse",
    "DeleteResponse",
    "ExistsResponse",
    "PetListResponse",
    "PetResponse",
    "PetSearchResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
