from typing import Any

from common.grpc_client.handlers.base import Handler
from common.proto.cloudevents_pb2 import CloudEvent


class AckHandler(Handler):
    async def handle(self, request: CloudEvent, services: Any = None) -> None:
        # No response; logs handled by LoggingMiddleware
        return None
