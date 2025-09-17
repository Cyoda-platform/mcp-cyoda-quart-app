"""
Models package for Purrfect Pets Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    AdoptionQueryParams,
    AdoptionUpdateQueryParams,
    OwnerQueryParams,
    OwnerUpdateQueryParams,
    PetQueryParams,
    PetUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
)
from .response_models import (
    AdoptionListResponse,
    AdoptionResponse,
    AdoptionSearchResponse,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    OwnerListResponse,
    OwnerResponse,
    OwnerSearchResponse,
    PetListResponse,
    PetResponse,
    PetSearchResponse,
    TransitionResponse,
    TransitionsResponse,
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
