"""
Models package for Pet Store Performance Analysis Application.

Provides request and response models for comprehensive API validation.
"""

from .request_models import (
    ProductQueryParams,
    ProductUpdateQueryParams,
    ReportQueryParams,
    ReportUpdateQueryParams,
    DataExtractionQueryParams,
    DataExtractionUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    ErrorResponse,
)
from .response_models import (
    ProductResponse,
    ProductListResponse,
    ProductSearchResponse,
    ReportResponse,
    ReportListResponse,
    ReportSearchResponse,
    DataExtractionResponse,
    DataExtractionListResponse,
    DataExtractionSearchResponse,
    CountResponse,
    DeleteResponse,
    ExistsResponse,
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
