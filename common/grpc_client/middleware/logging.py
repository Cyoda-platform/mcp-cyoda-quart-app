import json
import logging

from proto.cloudevents_pb2 import CloudEvent

from common.grpc_client.constants import (
    JOIN_EVENT_TYPE, EVENT_ACK_TYPE, CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE,
    GREET_EVENT_TYPE, KEEP_ALIVE_EVENT_TYPE, ERROR_EVENT_TYPE
)
from common.grpc_client.middleware.base import MiddlewareLink

logger = logging.getLogger(__name__)


class LoggingMiddleware(MiddlewareLink):
    async def handle(self, event: CloudEvent):
        # replicate log_incoming_event
        try:
            data = json.loads(event.text_data) if event.text_data else {}
            logger.info(f"[IN] Received event - Type: {event.type}, ID: {event.id}, Source: {event.source}")

            if event.type == EVENT_ACK_TYPE:
                source_event_id = data.get('sourceEventId', 'Unknown')
                success = data.get('success', 'Unknown')
                logger.info(f"[IN] EventAck - SourceEventId: {source_event_id}, Success: {success}")
            elif event.type in (CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE):
                entity_id = data.get('entityId', 'Unknown')
                request_id = data.get('requestId', 'Unknown')
                processor_name = data.get('processorName') or data.get('criteriaName', 'Unknown')
                logger.info(f"[IN] CalcRequest - EntityId: {entity_id}, RequestId: {request_id}, Processor: {processor_name}")
            elif event.type == GREET_EVENT_TYPE:
                logger.info(f"[IN] GreetEvent - Data: {data}")
            elif event.type == KEEP_ALIVE_EVENT_TYPE:
                event_id = data.get('id', 'Unknown')
                logger.debug(f"[IN] KeepAlive - EventId: {event_id}")
            elif event.type == ERROR_EVENT_TYPE:
                error_code = data.get('code', 'Unknown')
                error_message = data.get('message', 'Unknown')
                logger.error(f"[IN] ErrorEvent - Code: {error_code}, Message: {error_message}")
            else:
                logger.info(f"[IN] UnknownEvent - Data: {data}")

        except Exception as e:
            logger.warning(f"Failed to parse incoming event data: {e}")
            logger.info(f"[IN] Raw event - Type: {event.type}, ID: {event.id}, TextData: {event.text_data}")

        return await super().handle(event)

