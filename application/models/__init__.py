# application/models/__init__.py

"""
Models package for Pet Store Performance Analysis System API.
"""

from .request_models import (
    ProductQueryParams,
    ProductUpdateQueryParams,
    ReportQueryParams,
    ReportUpdateQueryParams,
    EmailNotificationQueryParams,
    EmailNotificationUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    ErrorResponse,
    ValidationErrorResponse
)

from .response_models import (
    ProductResponse,
    ProductListResponse,
    ProductSearchResponse,
    ReportResponse,
    ReportListResponse,
    ReportSearchResponse,
    EmailNotificationResponse,
    EmailNotificationListResponse,
    EmailNotificationSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    DeleteResponse,
    ExistsResponse,
    CountResponse
)

__all__ = [
    # Request models
    "ProductQueryParams",
    "ProductUpdateQueryParams",
    "ReportQueryParams", 
    "ReportUpdateQueryParams",
    "EmailNotificationQueryParams",
    "EmailNotificationUpdateQueryParams",
    "SearchRequest",
    "TransitionRequest",
    "ErrorResponse",
    "ValidationErrorResponse",
    
    # Response models
    "ProductResponse",
    "ProductListResponse",
    "ProductSearchResponse",
    "ReportResponse",
    "ReportListResponse", 
    "ReportSearchResponse",
    "EmailNotificationResponse",
    "EmailNotificationListResponse",
    "EmailNotificationSearchResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "DeleteResponse",
    "ExistsResponse",
    "CountResponse"
]
