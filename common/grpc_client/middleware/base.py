from typing import Any, Optional

from common.proto.cloudevents_pb2 import CloudEvent


class MiddlewareLink:
    def __init__(self) -> None:
        self._successor: Optional["MiddlewareLink"] = None

    def set_successor(self, nxt: "MiddlewareLink") -> "MiddlewareLink":
        self._successor = nxt
        return nxt

    async def handle(self, event: CloudEvent) -> Any:
        if self._successor:
            return await self._successor.handle(event)
        return None
