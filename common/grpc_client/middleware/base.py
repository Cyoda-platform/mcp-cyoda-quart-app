from proto.cloudevents_pb2 import CloudEvent


class MiddlewareLink:
    def __init__(self):
        self._successor: "MiddlewareLink | None" = None

    def set_successor(self, nxt: "MiddlewareLink") -> "MiddlewareLink":
        self._successor = nxt
        return nxt

    async def handle(self, event: CloudEvent):
        if self._successor:
            return await self._successor.handle(event)
        return None

