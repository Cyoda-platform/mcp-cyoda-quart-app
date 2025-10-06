# models/__init__.py

"""
Request and Response Models for Booking and Report API endpoints.
"""

from .request_models import (
    BookingQueryParams,
    BookingUpdateQueryParams,
    ReportQueryParams,
    ReportUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
)
from .response_models import (
    BookingListResponse,
    BookingResponse,
    BookingSearchResponse,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    ReportListResponse,
    ReportResponse,
    ReportSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "BookingQueryParams",
    "BookingUpdateQueryParams",
    "ReportQueryParams", 
    "ReportUpdateQueryParams",
    "SearchRequest",
    "TransitionRequest",
    # Response models
    "BookingListResponse",
    "BookingResponse",
    "BookingSearchResponse",
    "CountResponse",
    "DeleteResponse",
    "ErrorResponse",
    "ExistsResponse",
    "ReportListResponse",
    "ReportResponse",
    "ReportSearchResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
