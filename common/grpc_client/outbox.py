import asyncio
import json
import logging
import uuid
from typing import Optional

from proto.cloudevents_pb2 import CloudEvent
from common.grpc_client.constants import (
    JOIN_EVENT_TYPE, EVENT_ACK_TYPE, CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE,
    SPEC_VERSION, SOURCE, OWNER, TAGS
)
from common.grpc_client.responses.spec import ResponseSpec
from common.grpc_client.responses.builders import JoinResponseBuilder

logger = logging.getLogger(__name__)


class Outbox:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def send(self, response: CloudEvent) -> None:
        await self._queue.put(response)

    async def close(self) -> None:
        await self._queue.put(None)  # sentinel used by event_generator

    async def event_generator(self):
        """Generate outbound events: join first, then responses from queue."""
        # Send join event first
        join_spec = ResponseSpec(response_type=JOIN_EVENT_TYPE, data={})
        join_builder = JoinResponseBuilder()
        join_event = join_builder.build(join_spec)

        # Log join event
        try:
            data = json.loads(join_event.text_data) if join_event.text_data else {}
            logger.info(f"[OUT] Sending event - Type: {join_event.type}, ID: {join_event.id}, Source: {join_event.source}")
            owner = data.get('owner', 'Unknown')
            tags = data.get('tags', [])
            logger.info(f"[OUT] JoinEvent - Owner: {owner}, Tags: {tags}")
        except Exception as e:
            logger.warning(f"Failed to parse outgoing event data: {e}")
            logger.info(f"[OUT] Raw event - Type: {join_event.type}, ID: {join_event.id}, TextData: {join_event.text_data}")

        yield join_event

        # Then yield responses from queue
        while True:
            event = await self._queue.get()
            if event is None:
                break

            # Log outgoing event
            try:
                data = json.loads(event.text_data) if event.text_data else {}
                logger.info(f"[OUT] Sending event - Type: {event.type}, ID: {event.id}, Source: {event.source}")
                if event.type == EVENT_ACK_TYPE:
                    source_event_id = data.get('sourceEventId', 'Unknown')
                    success = data.get('success', 'Unknown')
                    logger.debug(f"[OUT] EventAck - SourceEventId: {source_event_id}, Success: {success}")
                elif event.type in (CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE):
                    entity_id = data.get('entityId', 'Unknown')
                    request_id = data.get('requestId', 'Unknown')
                    success = data.get('success', 'Unknown')
                    logger.info(f"[OUT] CalcResponse - EntityId: {entity_id}, RequestId: {request_id}, Success: {success}")
                else:
                    logger.info(f"[OUT] Event - Data: {data}")
            except Exception as e:
                logger.warning(f"Failed to parse outgoing event data: {e}")
                logger.info(f"[OUT] Raw event - Type: {event.type}, ID: {event.id}, TextData: {event.text_data}")

            yield event
            logger.debug(f"[OUT] Event completed - ID: {event.id}, Type: {event.type}")
            self._queue.task_done()

