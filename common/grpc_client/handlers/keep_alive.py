import json
from typing import Any

from common.grpc_client.constants import EVENT_ACK_TYPE
from common.grpc_client.handlers.base import Handler
from common.grpc_client.responses.spec import ResponseSpec
from common.proto.cloudevents_pb2 import CloudEvent


class KeepAliveHandler(Handler):
    async def handle(self, request: CloudEvent, services: Any = None) -> ResponseSpec:
        data = json.loads(request.text_data)
        return ResponseSpec(
            response_type=EVENT_ACK_TYPE,
            data={},
            source_event_id=data.get("id"),
            success=True,
        )
