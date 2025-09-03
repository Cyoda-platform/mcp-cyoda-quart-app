from proto.cloudevents_pb2 import CloudEvent
from common.grpc_client.responses.spec import ResponseSpec


class Handler:
    async def __call__(self, request: CloudEvent, services=None):
        return await self.handle(request, services)

    async def handle(self, request: CloudEvent, services=None) -> ResponseSpec:
        raise NotImplementedError

