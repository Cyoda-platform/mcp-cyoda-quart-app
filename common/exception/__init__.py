"""Exception handling module for the common package."""

from common.exception.exceptions import (
    ChatNotFoundError,
    ForbiddenAccessError,
    UnauthorizedAccessError,
)
from common.exception.grpc_exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    GrpcClientError,
    HandlerError,
    ProcessingError,
    ValidationError,
    handle_error,
    is_not_found,
)

__all__ = [
    # Base exceptions
    "ChatNotFoundError",
    "UnauthorizedAccessError",
    "ForbiddenAccessError",
    # gRPC exceptions
    "GrpcClientError",
    "ProcessingError",
    "HandlerError",
    "ConnectionError",
    "AuthenticationError",
    "ValidationError",
    "ConfigurationError",
    # Enums
    "ErrorSeverity",
    "ErrorCategory",
    # Utilities
    "ErrorHandler",
    "handle_error",
    "is_not_found",
]
