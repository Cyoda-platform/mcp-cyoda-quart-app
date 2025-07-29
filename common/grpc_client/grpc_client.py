import logging
import uuid
import json
import asyncio

import grpc

from cloudevents_pb2 import CloudEvent
from common.config import config
from common.config.config import GRPC_PROCESSOR_TAG
from cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub
from entity.workflow import process_dispatch, process_event

# These tags/configs from your original snippet
TAGS = [GRPC_PROCESSOR_TAG]
OWNER = "PLAY"
SPEC_VERSION = "1.0"
SOURCE = "SimpleSample"
JOIN_EVENT_TYPE = "CalculationMemberJoinEvent"
CALC_RESP_EVENT_TYPE = "EntityProcessorCalculationResponse"
CALC_REQ_EVENT_TYPE = "EntityProcessorCalculationRequest"
CRITERIA_CALC_REQ_EVENT_TYPE = "EntityCriteriaCalculationRequest"
CRITERIA_CALC_RESP_EVENT_TYPE = "EntityCriteriaCalculationResponse"
GREET_EVENT_TYPE = "CalculationMemberGreetEvent"
KEEP_ALIVE_EVENT_TYPE = "CalculationMemberKeepAliveEvent"
EVENT_ACK_TYPE = "EventAckResponse"
ERROR_EVENT_TYPE = "ErrorEvent"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrpcClient:
    def __init__(self, auth):
        self.auth = auth

    def metadata_callback(self, context, callback):
        """
        gRPC metadata provider that attaches a fresh Bearer token.
        If retrieving the token fails, it invalidates and retries once.
        """
        try:
            token = self.auth.get_access_token_sync()
        except Exception as e:
            logger.warning("Access‑token fetch failed, invalidating and retrying", exc_info=e)
            self.auth.invalidate_tokens()
            token = self.auth.get_access_token_sync()

        callback([('authorization', f'Bearer {token}')], None)

    def get_grpc_credentials(self) -> grpc.ChannelCredentials:
        """
        Create composite credentials: SSL + per‑call metadata token.
        """
        call_creds = grpc.metadata_call_credentials(self.metadata_callback)
        ssl_creds = grpc.ssl_channel_credentials()
        return grpc.composite_channel_credentials(ssl_creds, call_creds)

    def create_cloud_event(self, event_id: str, source: str, event_type: str, data: dict) -> CloudEvent:
        return CloudEvent(
            id=event_id,
            source=source,
            spec_version=SPEC_VERSION,
            type=event_type,
            text_data=json.dumps(data),
        )

    def create_join_event(self) -> CloudEvent:
        event_id = str(uuid.uuid4())
        return self.create_cloud_event(
            event_id=event_id,
            source=SOURCE,
            event_type=JOIN_EVENT_TYPE,
            data={
                "id": event_id,  # Required by BaseEvent schema
                "owner": OWNER,
                "tags": TAGS
            },
        )

    def create_notification_event(self, data: dict, type: str, response=None) -> CloudEvent:
        if type == CALC_REQ_EVENT_TYPE:
            event_id = str(uuid.uuid4())
            return self.create_cloud_event(
                event_id=event_id,
                source=SOURCE,
                event_type=CALC_RESP_EVENT_TYPE,
                data={
                    "id": event_id,  # Required by BaseEvent schema
                    "requestId": data.get('requestId'),
                    "entityId": data.get('entityId'),
                    "owner": OWNER,
                    "payload": data.get('payload'),
                    "success": True
                }
            )
        elif type == CRITERIA_CALC_REQ_EVENT_TYPE:
            event_id = str(uuid.uuid4())
            return self.create_cloud_event(
                event_id=event_id,
                source=SOURCE,
                event_type=CRITERIA_CALC_RESP_EVENT_TYPE,
                data={
                    "id": event_id,  # Required by BaseEvent schema
                    "requestId": data.get('requestId'),
                    "entityId": data.get('entityId'),
                    "owner": OWNER,
                    "matches": response,
                    "success": True
                }
            )
        else:
            raise ValueError(f"Unsupported notification type: {type}")

    def log_outgoing_event(self, event):
        """Log detailed information about outgoing events to server"""
        try:
            data = json.loads(event.text_data) if event.text_data else {}
            logger.info(f"[OUT] Sending event - Type: {event.type}, ID: {event.id}, Source: {event.source}")

            # Log specific details based on event type
            if event.type == JOIN_EVENT_TYPE:
                owner = data.get('owner', 'Unknown')
                tags = data.get('tags', [])
                logger.info(f"[OUT] JoinEvent - Owner: {owner}, Tags: {tags}")
            elif event.type == EVENT_ACK_TYPE:
                source_event_id = data.get('sourceEventId', 'Unknown')
                success = data.get('success', 'Unknown')
                logger.debug(f"[OUT] EventAck - SourceEventId: {source_event_id}, Success: {success}")
            elif event.type in (CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE):
                entity_id = data.get('entityId', 'Unknown')
                request_id = data.get('requestId', 'Unknown')
                success = data.get('success', 'Unknown')
                logger.info(f"[OUT] CalcResponse - EntityId: {entity_id}, RequestId: {request_id}, Success: {success}")
            else:
                logger.info(f"[OUT] Event - Data: {data}")

        except Exception as e:
            logger.warning(f"Failed to parse outgoing event data: {e}")
            logger.info(f"[OUT] Raw event - Type: {event.type}, ID: {event.id}, TextData: {event.text_data}")

    async def event_generator(self, queue: asyncio.Queue):
        join_event = self.create_join_event()
        self.log_outgoing_event(join_event)
        yield join_event

        while True:
            event = await queue.get()
            if event is None:
                break
            self.log_outgoing_event(event)
            yield event
            logger.debug(f"[OUT] Event completed - ID: {event.id}, Type: {event.type}")
            queue.task_done()

    async def handle_keep_alive_event(self, response, queue: asyncio.Queue):
        data = json.loads(response.text_data)
        event_id = str(uuid.uuid4())
        ack = self.create_cloud_event(
            event_id=event_id,
            source=SOURCE,
            event_type=EVENT_ACK_TYPE,
            data={
                "id": event_id,
                "sourceEventId": data.get('id'),
                "owner": OWNER,
                "success": True,
            },
        )
        logger.info(f"[OUT] Sending KeepAlive ACK - EventId: {event_id}, SourceEventId: {data.get('id')}")
        await queue.put(ack)

    async def handle_event_ack(self, response, queue: asyncio.Queue):
        data = json.loads(response.text_data)
        # Based on Java client, EVENT_ACK_RESPONSE events are processed but no response is sent
        source_event_id = data.get('sourceEventId')
        success = data.get('success', True)
        logger.debug(f"Received event ACK for event ID: {source_event_id}, success: {success}")
        # No response event is created for EVENT_ACK_RESPONSE based on Java client pattern

    async def handle_greet_event(self, response, queue: asyncio.Queue):
        data = json.loads(response.text_data)
        # Based on Java client, GREET_EVENT is processed but no response is sent
        logger.info(f"Received greet event: {data}")

    async def handle_error_event(self, response, queue: asyncio.Queue):
        data = json.loads(response.text_data)
        error_message = data.get('message', 'Unknown error')
        error_code = data.get('code', 'UNKNOWN')
        source_event_id = data.get('sourceEventId', 'Unknown')
        logger.error(f"Server error event received - Code: {error_code}, Message: {error_message}, SourceEventId: {source_event_id}")
        logger.error(f"Full error event data: {data}")
        # No response event is created for error events

    def log_incoming_event(self, response):
        """Log detailed information about incoming events from server"""
        try:
            data = json.loads(response.text_data) if response.text_data else {}
            logger.info(f"[IN] Received event - Type: {response.type}, ID: {response.id}, Source: {response.source}")

            # Log specific details based on event type
            if response.type == EVENT_ACK_TYPE:
                source_event_id = data.get('sourceEventId', 'Unknown')
                success = data.get('success', 'Unknown')
                logger.info(f"[IN] EventAck - SourceEventId: {source_event_id}, Success: {success}")
            elif response.type in (CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE):
                entity_id = data.get('entityId', 'Unknown')
                request_id = data.get('requestId', 'Unknown')
                processor_name = data.get('processorName') or data.get('criteriaName', 'Unknown')
                logger.info(f"[IN] CalcRequest - EntityId: {entity_id}, RequestId: {request_id}, Processor: {processor_name}")
            elif response.type == GREET_EVENT_TYPE:
                logger.info(f"[IN] GreetEvent - Data: {data}")
            elif response.type == KEEP_ALIVE_EVENT_TYPE:
                event_id = data.get('id', 'Unknown')
                logger.debug(f"[IN] KeepAlive - EventId: {event_id}")
            elif response.type == ERROR_EVENT_TYPE:
                error_code = data.get('code', 'Unknown')
                error_message = data.get('message', 'Unknown')
                logger.error(f"[IN] ErrorEvent - Code: {error_code}, Message: {error_message}")
            else:
                logger.info(f"[IN] UnknownEvent - Data: {data}")

        except Exception as e:
            logger.warning(f"Failed to parse incoming event data: {e}")
            logger.info(f"[IN] Raw event - Type: {response.type}, ID: {response.id}, TextData: {response.text_data}")

    async def process_calc_req_event(self, data: dict, queue: asyncio.Queue, type: str):
        if type == CALC_REQ_EVENT_TYPE:
            processor_name = data.get('processorName')
        elif type == CRITERIA_CALC_REQ_EVENT_TYPE:
            processor_name = data.get('criteriaName')
        else:
            raise ValueError(f"Unsupported event type: {type}")
        try:
            # Process the first or subsequent versions of the entity
            if processor_name in process_dispatch:
                logger.debug(f"Processing notification entity: {data}")
                await process_event(data=data, processor_name=processor_name)

        except Exception as e:
            logger.error(e)
        #Create notification event and put it in the queue
        notification_event = self.create_notification_event(data=data, type=type)
        await queue.put(notification_event)

    async def consume_stream(self):
        backoff = 1
        while True:
            creds = self.get_grpc_credentials()
            queue = asyncio.Queue()

            try:
                # 1) Define keep-alive options (milliseconds unless noted)
                keepalive_opts = [
                    ('grpc.keepalive_time_ms', 15_000),  # PING every 30 s
                    ('grpc.keepalive_timeout_ms', 30_000),  # wait 10 s for PONG
                    ('grpc.keepalive_permit_without_calls', 1),  # even if idle
                    ('grpc.enable_http_proxy', 0),
                    ("grpc.max_send_message_length", 100 * 1024 * 1024),     # e.g., 100MB
                    ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                ]

                # 2) Pass them into secure_channel alongside your creds
                async with grpc.aio.secure_channel(
                        config.GRPC_ADDRESS,
                        creds,
                        options=keepalive_opts
                ) as channel:
                    stub = CloudEventsServiceStub(channel)
                    call = stub.startStreaming(self.event_generator(queue))
                    # … then await call or iterate its stream as needed

                    async for response in call:
                        # Log all incoming events for debugging
                        self.log_incoming_event(response)

                        if response.type == KEEP_ALIVE_EVENT_TYPE:
                            asyncio.create_task(self.handle_keep_alive_event(response, queue))
                        elif response.type == EVENT_ACK_TYPE:
                            asyncio.create_task(self.handle_event_ack(response, queue))
                        elif response.type in (CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE):
                            logger.info(f"Calc request: {response.type}")
                            data = json.loads(response.text_data)
                            asyncio.create_task(self.process_calc_req_event(data, queue, response.type))
                        elif response.type == GREET_EVENT_TYPE:
                            asyncio.create_task(self.handle_greet_event(response, queue))
                        elif response.type == ERROR_EVENT_TYPE:
                            asyncio.create_task(self.handle_error_event(response, queue))
                        else:
                            logger.error(f"Unhandled event type: {response.type}")
                            logger.error(f"Unhandled event details - ID: {response.id}, Source: {response.source}, Data: {response.text_data}")

                # If we exit the stream cleanly, break out of the retry loop
                logger.info("Stream closed by server—reconnecting")
                backoff = 1  # reset your backoff if you like
                continue

            except grpc.RpcError as e:
                # Enhanced gRPC error logging
                error_code = getattr(e, "code", lambda: None)()
                error_details = getattr(e, "details", lambda: "No details")()
                error_debug_string = getattr(e, "debug_error_string", lambda: "No debug info")()

                logger.error(f"gRPC RpcError - Code: {error_code}, Details: {error_details}")
                logger.error(f"gRPC Debug Info: {error_debug_string}")
                logger.exception("Full gRPC exception:", exc_info=e)

                # UNAUTHENTICATED → invalidate tokens, then retry with fresh creds
                if error_code == grpc.StatusCode.UNAUTHENTICATED:
                    logger.warning(
                        "Stream got UNAUTHENTICATED—invalidating tokens and retrying",
                        exc_info=e,
                    )
                    self.auth.invalidate_tokens()
                else:
                    # Log everything else and retry
                    logger.exception("gRPC RpcError in consume_stream", exc_info=e)


            except Exception as e:
                # Catch-all for anything unexpected
                logger.exception(e)
                logger.exception("Unexpected error in consume_stream", exc_info=e)

            # back off and retry
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)  # exponential backoff up to 30s

    async def grpc_stream(self):
        """
        Entry point: keeps the bidirectional stream alive, reconnecting on token revocations.
        """
        try:
            await self.consume_stream()
        except Exception as e:
            logger.exception(e)
