"""
Models package for Application.

Provides request and response models for Task API validation.
"""

from .request_models import (
    TaskQueryParams,
    TaskUpdateQueryParams,
)
from .response_models import (
    TaskResponse,
    TaskListResponse,
    TaskSearchResponse,
)

# Import common models from example_application
from example_application.models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

__all__ = [
    # Task-specific models
    "TaskQueryParams",
    "TaskUpdateQueryParams",
    "TaskResponse",
    "TaskListResponse",
    "TaskSearchResponse",
    # Common models
    "CountResponse",
    "DeleteResponse",
    "ErrorResponse",
    "ExistsResponse",
    "SearchRequest",
    "TransitionRequest",
    "TransitionResponse",
    "TransitionsResponse",
    "ValidationErrorResponse",
]
