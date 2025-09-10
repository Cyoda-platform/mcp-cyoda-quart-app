import asyncio
import json
import logging
from typing import Any

from common.grpc_client.handlers.base import Handler
from common.proto.cloudevents_pb2 import CloudEvent

logger = logging.getLogger(__name__)


class GreetHandler(Handler):
    async def handle(self, request: CloudEvent, services: Any = None) -> None:
        data = json.loads(request.text_data)
        logger.info(f"Received greet event: {data}")

        # Restart failed workflows when greet event is received
        if (
            services
            and hasattr(services, "chat_service")
            and hasattr(services, "processor_loop")
        ):
            logger.info("restarting entities workflows....")
            try:
                services.processor_loop.run_coroutine(
                    self._restart_failed_workflows(services.chat_service)
                )
            except Exception as e:
                logger.error("Failed to restart entities")
                logger.exception(e)

        return None

    async def _restart_failed_workflows(self, chat_service: Any) -> None:
        """Restart failed workflows."""
        try:
            asyncio.create_task(chat_service.rollback_failed_workflows())
        except Exception as e:
            logger.error("Failed to restart entities")
            logger.exception(e)
