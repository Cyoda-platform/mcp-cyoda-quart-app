from typing import Any, Optional

from common.grpc_client.responses.spec import ResponseSpec
from common.proto.cloudevents_pb2 import CloudEvent


class Handler:
    async def __call__(
        self, request: CloudEvent, services: Optional[Any] = None
    ) -> Optional[ResponseSpec]:
        return await self.handle(request, services)

    async def handle(
        self, request: CloudEvent, services: Optional[Any] = None
    ) -> Optional[ResponseSpec]:
        raise NotImplementedError
