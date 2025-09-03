import json
import logging

from proto.cloudevents_pb2 import CloudEvent

from common.grpc_client.middleware.base import MiddlewareLink
from common.grpc_client.responses.spec import ResponseSpec
from common.grpc_client.responses.builders import ResponseBuilderRegistry
from common.grpc_client.router import EventRouter
from common.grpc_client.outbox import Outbox
from common.grpc_client.constants import EVENT_ACK_TYPE

logger = logging.getLogger(__name__)


class DispatchMiddleware(MiddlewareLink):
    def __init__(self, router: EventRouter, builders: ResponseBuilderRegistry, outbox: Outbox, services=None):
        super().__init__()
        self._router = router
        self._builders = builders
        self._outbox = outbox
        self._services = services

    async def handle(self, event: CloudEvent):
        handler = self._router.route(event)
        if not handler:
            logger.error(f"Unhandled event type: {event.type}")
            logger.error(f"Unhandled event details - ID: {event.id}, Source: {event.source}, Data: {event.text_data}")
            return None

        spec: ResponseSpec | None = await handler(event, self._services)
        if spec is None:
            return None

        builder = self._builders.get(spec.response_type)
        response = builder.build(spec)

        # Special parity log for KeepAlive ACK
        if response.type == EVENT_ACK_TYPE:
            try:
                data = json.loads(response.text_data) if response.text_data else {}
                logger.info(f"[OUT] Sending KeepAlive ACK - EventId: {response.id}, SourceEventId: {data.get('sourceEventId')}")
            except Exception as e:
                logger.warning(f"Failed to parse outgoing event data: {e}")

        # Do not duplicate general OUT logs here; event_generator() logs them
        await self._outbox.send(response)
        return None

