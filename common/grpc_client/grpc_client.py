"""
Simple, dull GrpcClient for backward compatibility.
All complex logic has been moved to factory.py and legacy_methods.py.
"""
import logging
import asyncio

import grpc
from proto.cloudevents_pb2 import CloudEvent
from common.utils.event_loop import BackgroundEventLoop

# Import constants for backward compatibility
from common.grpc_client.constants import (
    TAGS, OWNER, SPEC_VERSION, SOURCE,
    JOIN_EVENT_TYPE, CALC_RESP_EVENT_TYPE, CALC_REQ_EVENT_TYPE,
    CRITERIA_CALC_REQ_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE,
    GREET_EVENT_TYPE, KEEP_ALIVE_EVENT_TYPE, EVENT_ACK_TYPE, ERROR_EVENT_TYPE,
)

logger = logging.getLogger(__name__)


class GrpcClient:
    """
    Dull wrapper class for backward compatibility.
    All logic moved elsewhere - this just delegates.
    """
    def __init__(self, auth ):
        # Store dependencies
        self.auth = auth
        self.processor_loop = BackgroundEventLoop()

        # Lazy initialization
        self._facade = None

    def _get_facade(self):
        """Get facade, creating it if needed."""
        if self._facade is None:
            from common.grpc_client.factory import GrpcStreamingFacadeFactory
            self._facade = GrpcStreamingFacadeFactory.create(
                auth=self.auth,
                processor_loop=self.processor_loop,
                grpc_client=self
            )
        return self._facade


    # Main entry points - simple delegation
    async def grpc_stream(self):
        """Entry point."""
        try:
            await self._get_facade().start()
        except Exception as e:
            logger.exception(e)


# Re-export constants for backward compatibility
__all__ = [
    'GrpcClient', 'TAGS', 'OWNER', 'SPEC_VERSION', 'SOURCE',
    'JOIN_EVENT_TYPE', 'CALC_RESP_EVENT_TYPE', 'CALC_REQ_EVENT_TYPE',
    'CRITERIA_CALC_REQ_EVENT_TYPE', 'CRITERIA_CALC_RESP_EVENT_TYPE',
    'GREET_EVENT_TYPE', 'KEEP_ALIVE_EVENT_TYPE', 'EVENT_ACK_TYPE', 'ERROR_EVENT_TYPE'
]
