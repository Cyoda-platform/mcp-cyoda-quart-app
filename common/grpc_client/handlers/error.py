import json
import logging

from common.grpc_client.handlers.base import Handler
from proto.cloudevents_pb2 import CloudEvent

logger = logging.getLogger(__name__)


class ErrorHandler(Handler):
    async def handle(self, request: CloudEvent, services=None):
        data = json.loads(request.text_data)
        error_message = data.get("message", "Unknown error")
        error_code = data.get("code", "UNKNOWN")
        source_event_id = data.get("sourceEventId", "Unknown")
        logger.error(
            f"Server error event received - Code: {error_code}, Message: {error_message}, SourceEventId: {source_event_id}"
        )
        logger.error(f"Full error event data: {data}")
        return None
