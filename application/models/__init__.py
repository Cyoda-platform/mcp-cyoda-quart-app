"""
Models package for Purrfect Pets Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    PetQueryParams,
    PetUpdateQueryParams,
    OwnerQueryParams,
    OwnerUpdateQueryParams,
    AdoptionQueryParams,
    AdoptionUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
)
from .response_models import (
    PetResponse,
    PetListResponse,
    PetSearchResponse,
    OwnerResponse,
    OwnerListResponse,
    OwnerSearchResponse,
    AdoptionResponse,
    AdoptionListResponse,
    AdoptionSearchResponse,
    CountResponse,
    DeleteResponse,
    ExistsResponse,
    TransitionResponse,
    TransitionsResponse,
    ErrorResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "PetQueryParams",
    "PetUpdateQueryParams",
    "OwnerQueryParams",
    "OwnerUpdateQueryParams",
    "AdoptionQueryParams",
    "AdoptionUpdateQueryParams",
    "SearchRequest",
    "TransitionRequest",
    # Response models
    "PetResponse",
    "PetListResponse",
    "PetSearchResponse",
    "OwnerResponse",
    "OwnerListResponse",
    "OwnerSearchResponse",
    "AdoptionResponse",
    "AdoptionListResponse",
    "AdoptionSearchResponse",
    "CountResponse",
    "DeleteResponse",
    "ExistsResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
]
