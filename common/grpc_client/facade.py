from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable, Sequence
from typing import Any, Optional, Tuple, cast

import grpc

from common.config.config import GRPC_ADDRESS, SKIP_SSL
from common.grpc_client.middleware.base import MiddlewareLink
from common.grpc_client.outbox import Outbox
from common.grpc_client.responses.builders import ResponseBuilderRegistry
from common.grpc_client.router import EventRouter
from common.proto.cloudevents_pb2 import CloudEvent
from common.proto.cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub

logger = logging.getLogger(__name__)


class GrpcStreamingFacade:
    def __init__(
        self,
        auth: Any,
        router: EventRouter,
        builders: ResponseBuilderRegistry,
        outbox: Outbox,
        first_middleware: MiddlewareLink,
        grpc_client: Any | None = None,
    ) -> None:
        self.auth = auth
        self.router = router
        self.builders = builders
        self.outbox = outbox
        self.first_middleware = first_middleware
        # Reference to original GrpcClient for backward compatibility
        self.grpc_client = grpc_client
        self._running: bool = False

    def metadata_callback(
        self,
        context: grpc.AuthMetadataContext,
        callback: Callable[[Sequence[Tuple[str, str]], Optional[BaseException]], None],
    ) -> None:
        """gRPC metadata provider that attaches a fresh Bearer token."""
        try:
            token: str = self.auth.get_access_token_sync()
        except Exception as e:  # noqa: BLE001 - bubble up with logging
            logger.exception(e)
            logger.warning(
                "Access-token fetch failed, invalidating and retrying", exc_info=e
            )
            self.auth.invalidate_tokens()
            token = self.auth.get_access_token_sync()

        callback([("authorization", f"Bearer {token}")], None)

    def get_grpc_credentials(self) -> grpc.ChannelCredentials:
        """Create composite credentials: SSL + per-call metadata token."""
        call_creds: grpc.CallCredentials = grpc.metadata_call_credentials(
            self.metadata_callback
        )

        ssl_creds = (
            grpc.local_channel_credentials()
            if SKIP_SSL
            else grpc.ssl_channel_credentials()
        )
        return grpc.composite_channel_credentials(ssl_creds, call_creds)

    def _on_event(self, event: CloudEvent) -> None:
        """Process inbound event through middleware chain."""
        asyncio.create_task(self.first_middleware.handle(event))

    async def start(self) -> None:
        """Start the gRPC streaming connection."""
        self._running = True
        await self._consume_stream()

    def stop(self) -> None:
        """Stop the gRPC streaming connection."""
        self._running = False
        asyncio.create_task(self.outbox.close())

    async def _consume_stream(self) -> None:
        """Main streaming loop with reconnection and backoff."""
        backoff: int = 1
        while self._running:
            creds = self.get_grpc_credentials()

            try:
                keepalive_opts: list[tuple[str, int]] = [
                    ("grpc.keepalive_time_ms", 15_000),
                    ("grpc.keepalive_timeout_ms", 30_000),
                    ("grpc.keepalive_permit_without_calls", 1),
                    ("grpc.enable_http_proxy", 0),
                    ("grpc.max_send_message_length", 100 * 1024 * 1024),
                    ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                ]

                async with grpc.aio.secure_channel(
                    GRPC_ADDRESS, creds, options=keepalive_opts
                ) as channel:
                    # Generated stubs are untyped; suppress no-untyped-call for this line.
                    stub: Any = CloudEventsServiceStub(channel)  # type: ignore[no-untyped-call]
                    call: AsyncIterator[CloudEvent] = stub.startStreaming(
                        self.outbox.event_generator()
                    )

                    async for response in call:
                        if not self._running:
                            break
                        self._on_event(response)

                if self._running:
                    logger.info("Stream closed by server—reconnecting")
                    backoff = 1
                    continue
                else:
                    break

            except grpc.RpcError as e:
                if not self._running:
                    break

                # Accessors on RpcError are runtime methods; be defensive for typing.
                error_code: Optional[grpc.StatusCode] = getattr(
                    e, "code", lambda: None
                )()
                error_details: str = cast(
                    str, getattr(e, "details", lambda: "No details")()
                )
                error_debug_string: str = cast(
                    str, getattr(e, "debug_error_string", lambda: "No debug info")()
                )

                logger.error(
                    f"gRPC RpcError - Code: {error_code}, Details: {error_details}"
                )
                logger.error(f"gRPC Debug Info: {error_debug_string}")
                logger.exception("Full gRPC exception:", exc_info=e)

                if error_code == grpc.StatusCode.UNAUTHENTICATED:
                    logger.warning(
                        "Stream got UNAUTHENTICATED—invalidating tokens and retrying",
                        exc_info=e,
                    )
                    self.auth.invalidate_tokens()
                else:
                    logger.exception("gRPC RpcError in consume_stream", exc_info=e)

            except Exception as e:  # noqa: BLE001 - capture and continue with backoff
                if not self._running:
                    break
                logger.exception(e)
                logger.exception("Unexpected error in consume_stream", exc_info=e)

            if self._running:
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
