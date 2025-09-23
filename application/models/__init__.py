# models/__init__.py

"""
Request and Response models for Pet Store Performance Analysis System API
"""

from .request_models import (
    DataExtractionQueryParams,
    DataExtractionUpdateQueryParams,
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
    ErrorResponse,
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
    "ErrorResponse",
    "ExistsResponse",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
