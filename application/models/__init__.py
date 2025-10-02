"""
Models package for Cat Fact Subscription Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    CatFactQueryParams,
    CatFactUpdateQueryParams,
    EmailCampaignQueryParams,
    EmailCampaignUpdateQueryParams,
    ErrorResponse,
    SearchRequest,
    SubscriberQueryParams,
    SubscriberUpdateQueryParams,
    SuccessResponse,
    TransitionRequest,
)
from .response_models import (
    CatFactListResponse,
    CatFactResponse,
    CatFactSearchResponse,
    CountResponse,
    DeleteResponse,
    EmailCampaignListResponse,
    EmailCampaignResponse,
    EmailCampaignSearchResponse,
)
from .response_models import ErrorResponse as ResponseErrorResponse
from .response_models import (
    ExistsResponse,
    HealthResponse,
    StatusResponse,
    SubscriberListResponse,
    SubscriberResponse,
    SubscriberSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "CatFactQueryParams",
    "CatFactUpdateQueryParams",
    "EmailCampaignQueryParams",
    "EmailCampaignUpdateQueryParams",
    "ErrorResponse",
    "SearchRequest",
    "SubscriberQueryParams",
    "SubscriberUpdateQueryParams",
    "SuccessResponse",
    "TransitionRequest",
    # Response models
    "CatFactListResponse",
    "CatFactResponse",
    "CatFactSearchResponse",
    "CountResponse",
    "DeleteResponse",
    "EmailCampaignListResponse",
    "EmailCampaignResponse",
    "EmailCampaignSearchResponse",
    "ExistsResponse",
    "HealthResponse",
    "ResponseErrorResponse",
    "StatusResponse",
    "SubscriberListResponse",
    "SubscriberResponse",
    "SubscriberSearchResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
