import logging
from typing import Optional

from proto.cloudevents_pb2 import CloudEvent

from common.grpc_client.middleware.base import MiddlewareLink
from common.exception.grpc_exceptions import (
    ErrorHandler, HandlerError, GrpcClientError
)

logger = logging.getLogger(__name__)


class ErrorMiddleware(MiddlewareLink):
    """Enhanced error middleware with comprehensive error handling."""

    def __init__(self):
        super().__init__()
        self.error_handler = ErrorHandler(logger)

    async def handle(self, event: CloudEvent):
        try:
            return await super().handle(event)
        except GrpcClientError as e:
            # Already a proper gRPC error, just handle it
            self.error_handler.handle_error(e)
            return self._create_error_response(e, event)
        except Exception as e:
            # Convert to proper error and handle
            grpc_error = HandlerError(
                handler_name="unknown",
                event_type=event.type,
                event_id=event.id,
                message=str(e),
                original_error=e
            )
            self.error_handler.handle_error(grpc_error)
            return self._create_error_response(grpc_error, event)

    def _create_error_response(
        self,
        error: GrpcClientError,
        event: CloudEvent
    ) -> Optional[dict]:
        """
        Create error response based on error type and recoverability.

        Args:
            error: The error that occurred
            event: The original event

        Returns:
            Error response dict or None if no response should be sent
        """
        # For now, preserve current behavior: do not emit error responses
        # This can be enhanced later to send error responses for certain error types
        return None

