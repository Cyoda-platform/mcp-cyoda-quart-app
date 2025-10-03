"""
Models package for Pet Store Performance Analysis Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    DataExtractionQueryParams,
    DataExtractionUpdateQueryParams,
    ErrorResponse,
    ProductQueryParams,
    ProductUpdateQueryParams,
    ReportQueryParams,
    ReportUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
)
from .response_models import (
    CountResponse,
    DataExtractionListResponse,
    DataExtractionResponse,
    DataExtractionSearchResponse,
    DeleteResponse,
    ExistsResponse,
    ProductListResponse,
    ProductResponse,
    ProductSearchResponse,
    ReportListResponse,
    ReportResponse,
    ReportSearchResponse,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Request models
    "ProductQueryParams",
    "ProductUpdateQueryParams",
    "ReportQueryParams",
    "ReportUpdateQueryParams",
    "DataExtractionQueryParams",
    "DataExtractionUpdateQueryParams",
    "SearchRequest",
    "TransitionRequest",
    "ErrorResponse",
    # Response models
    "ProductResponse",
    "ProductListResponse",
    "ProductSearchResponse",
    "ReportResponse",
    "ReportListResponse",
    "ReportSearchResponse",
    "DataExtractionResponse",
    "DataExtractionListResponse",
    "DataExtractionSearchResponse",
    "CountResponse",
    "DeleteResponse",
    "ExistsResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
