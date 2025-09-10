from common.grpc_client.handlers.base import Handler
from proto.cloudevents_pb2 import CloudEvent


class AckHandler(Handler):
    async def handle(self, request: CloudEvent, services=None):
        # No response; logs handled by LoggingMiddleware
        return None
