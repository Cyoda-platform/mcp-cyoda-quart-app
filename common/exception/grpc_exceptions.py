"""
Enhanced exception handling for gRPC client system.

This module provides comprehensive error handling with proper error types,
context information, and recovery mechanisms.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for proper handling and logging."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors for better classification."""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    PROCESSING = "processing"
    CONFIGURATION = "configuration"
    SYSTEM = "system"


class GrpcClientError(Exception):
    """Base exception for all gRPC client related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
        recoverable: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.original_error = original_error
        self.recoverable = recoverable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "recoverable": self.recoverable,
            "original_error": str(self.original_error) if self.original_error else None
        }


class ProcessingError(GrpcClientError):
    """Error during entity processing."""
    
    def __init__(
        self,
        processor_name: str,
        entity_id: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Processing failed for processor '{processor_name}' on entity '{entity_id}': {message}",
            error_code="PROCESSING_FAILED",
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.HIGH,
            context={
                "processor_name": processor_name,
                "entity_id": entity_id
            },
            original_error=original_error,
            recoverable=True
        )
        self.processor_name = processor_name
        self.entity_id = entity_id


class HandlerError(GrpcClientError):
    """Error in event handler processing."""
    
    def __init__(
        self,
        handler_name: str,
        event_type: str,
        event_id: str,
        message: str,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Handler '{handler_name}' failed for event '{event_type}' (ID: {event_id}): {message}",
            error_code="HANDLER_FAILED",
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.HIGH,
            context={
                "handler_name": handler_name,
                "event_type": event_type,
                "event_id": event_id
            },
            original_error=original_error,
            recoverable=True
        )
        self.handler_name = handler_name
        self.event_type = event_type
        self.event_id = event_id


class ConnectionError(GrpcClientError):
    """gRPC connection related errors."""
    
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Connection error{f' to {endpoint}' if endpoint else ''}: {message}",
            error_code="CONNECTION_FAILED",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.CRITICAL,
            context={"endpoint": endpoint} if endpoint else {},
            original_error=original_error,
            recoverable=True
        )
        self.endpoint = endpoint


class AuthenticationError(GrpcClientError):
    """Authentication related errors."""
    
    def __init__(
        self,
        message: str,
        auth_method: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Authentication failed{f' for {auth_method}' if auth_method else ''}: {message}",
            error_code="AUTH_FAILED",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            context={"auth_method": auth_method} if auth_method else {},
            original_error=original_error,
            recoverable=False
        )
        self.auth_method = auth_method


class ValidationError(GrpcClientError):
    """Data validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Validation failed{f' for field {field_name}' if field_name else ''}: {message}",
            error_code="VALIDATION_FAILED",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context={
                "field_name": field_name,
                "field_value": str(field_value) if field_value is not None else None
            } if field_name else {},
            original_error=original_error,
            recoverable=False
        )
        self.field_name = field_name
        self.field_value = field_value


class ConfigurationError(GrpcClientError):
    """Configuration related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"Configuration error{f' for {config_key}' if config_key else ''}: {message}",
            error_code="CONFIG_ERROR",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            context={"config_key": config_key} if config_key else {},
            original_error=original_error,
            recoverable=False
        )
        self.config_key = config_key


class ErrorHandler:
    """Centralized error handler with logging and recovery mechanisms."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> GrpcClientError:
        """
        Handle any error and convert to appropriate GrpcClientError.
        
        Args:
            error: The original error
            context: Additional context information
            
        Returns:
            Appropriate GrpcClientError instance
        """
        if isinstance(error, GrpcClientError):
            # Already a proper error, just log it
            self._log_error(error)
            return error
        
        # Convert generic error to GrpcClientError
        grpc_error = GrpcClientError(
            message=str(error),
            error_code="GENERIC_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context or {},
            original_error=error,
            recoverable=True
        )
        
        self._log_error(grpc_error)
        return grpc_error
    
    def _log_error(self, error: GrpcClientError) -> None:
        """Log error with appropriate level based on severity."""
        error_dict = error.to_dict()
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical("Critical error occurred", extra={"error": error_dict})
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error("High severity error occurred", extra={"error": error_dict})
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning("Medium severity error occurred", extra={"error": error_dict})
        else:
            self.logger.info("Low severity error occurred", extra={"error": error_dict})
        
        # Log original exception if present
        if error.original_error:
            self.logger.exception("Original exception details", exc_info=error.original_error)


# Global error handler instance
_error_handler = ErrorHandler()


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> GrpcClientError:
    """Convenience function to handle errors using global handler."""
    return _error_handler.handle_error(error, context)
