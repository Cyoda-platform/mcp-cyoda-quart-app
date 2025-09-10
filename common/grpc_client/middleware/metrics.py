"""
Simplified metrics middleware - no-op for simplicity.
"""

import logging
from typing import Any

from common.proto.cloudevents_pb2 import CloudEvent

from .base import MiddlewareLink

logger = logging.getLogger(__name__)


class MetricsMiddleware(MiddlewareLink):
    """Simplified metrics middleware - no-op for simplicity."""

    def __init__(self) -> None:
        super().__init__()

    async def handle(self, event: CloudEvent) -> Any:
        """Handle event without metrics collection."""
        # Simply pass through to the next middleware
        return await super().handle(event)
