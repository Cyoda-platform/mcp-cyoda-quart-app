from typing import Callable, Dict

from proto.cloudevents_pb2 import CloudEvent


class EventRouter:
    def __init__(self):
        self._handlers: Dict[str, Callable[[CloudEvent], None]] = {}

    def register(self, event_type: str, handler: Callable[[CloudEvent], None]) -> None:
        self._handlers[event_type] = handler

    def route(self, event: CloudEvent):
        return self._handlers.get(event.type)

