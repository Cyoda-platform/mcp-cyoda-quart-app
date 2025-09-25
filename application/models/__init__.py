# application/models/__init__.py

"""
Models package for Pet Store Performance Analysis System API.
"""

from .request_models import (
    EmailNotificationQueryParams,
    EmailNotificationUpdateQueryParams,
    ErrorResponse,
    ProductQueryParams,
    ProductUpdateQueryParams,
    ReportQueryParams,
    ReportUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    ValidationErrorResponse,
)
from .response_models import (
    CountResponse,
    DeleteResponse,
    EmailNotificationListResponse,
    EmailNotificationResponse,
    EmailNotificationSearchResponse,
    ExistsResponse,
    ProductListResponse,
    ProductResponse,
    ProductSearchResponse,
    ReportListResponse,
    ReportResponse,
    ReportSearchResponse,
    TransitionResponse,
    TransitionsResponse,
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
    "CountResponse",
]
