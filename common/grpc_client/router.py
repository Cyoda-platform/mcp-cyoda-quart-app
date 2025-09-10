from typing import Any, Dict, Optional

from common.proto.cloudevents_pb2 import CloudEvent


class EventRouter:
    def __init__(self) -> None:
        self._handlers: Dict[str, Any] = {}

    def register(self, event_type: str, handler: Any) -> None:
        self._handlers[event_type] = handler

    def route(self, event: CloudEvent) -> Optional[Any]:
        return self._handlers.get(event.type)
