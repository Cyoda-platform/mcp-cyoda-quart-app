import json
import uuid
from typing import Dict

from proto.cloudevents_pb2 import CloudEvent

from common.grpc_client.constants import (
    SPEC_VERSION, SOURCE, OWNER, TAGS,
    CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE, EVENT_ACK_TYPE, JOIN_EVENT_TYPE
)
from common.grpc_client.responses.spec import ResponseSpec


class ResponseBuilder:
    def build(self, spec: ResponseSpec) -> CloudEvent:
        raise NotImplementedError


class ResponseBuilderRegistry:
    def __init__(self):
        self._builders: Dict[str, ResponseBuilder] = {}

    def register(self, response_type: str, builder: ResponseBuilder) -> None:
        self._builders[response_type] = builder

    def get(self, response_type: str) -> ResponseBuilder:
        builder = self._builders.get(response_type)
        if not builder:
            raise KeyError(f"No builder registered for response_type: {response_type}")
        return builder


class AckResponseBuilder(ResponseBuilder):
    def build(self, spec: ResponseSpec) -> CloudEvent:
        event_id = str(uuid.uuid4())
        return CloudEvent(
            id=event_id,
            source=SOURCE,
            spec_version=SPEC_VERSION,
            type=EVENT_ACK_TYPE,
            text_data=json.dumps({
                "id": event_id,
                "sourceEventId": spec.source_event_id,
                "owner": OWNER,
                "success": True,
            }),
        )


class JoinResponseBuilder(ResponseBuilder):
    def build(self, spec: ResponseSpec) -> CloudEvent:
        # spec.data expected empty; we generate same join as before
        event_id = str(uuid.uuid4())
        return CloudEvent(
            id=event_id,
            source=SOURCE,
            spec_version=SPEC_VERSION,
            type=JOIN_EVENT_TYPE,
            text_data=json.dumps({
                "id": event_id,
                "owner": OWNER,
                "tags": TAGS,
            }),
        )


class CalcResponseBuilder(ResponseBuilder):
    def build(self, spec: ResponseSpec) -> CloudEvent:
        event_id = str(uuid.uuid4())
        data = spec.data
        return CloudEvent(
            id=event_id,
            source=SOURCE,
            spec_version=SPEC_VERSION,
            type=CALC_RESP_EVENT_TYPE,
            text_data=json.dumps({
                "id": event_id,
                "requestId": data.get("requestId"),
                "entityId": data.get("entityId"),
                "owner": OWNER,
                "payload": data.get("payload"),
                "success": True,
            }),
        )


class CriteriaCalcResponseBuilder(ResponseBuilder):
    def build(self, spec: ResponseSpec) -> CloudEvent:
        event_id = str(uuid.uuid4())
        data = spec.data
        return CloudEvent(
            id=event_id,
            source=SOURCE,
            spec_version=SPEC_VERSION,
            type=CRITERIA_CALC_RESP_EVENT_TYPE,
            text_data=json.dumps({
                "id": event_id,
                "requestId": data.get("requestId"),
                "entityId": data.get("entityId"),
                "owner": OWNER,
                "matches": data.get("matches"),
                "success": True,
            }),
        )

