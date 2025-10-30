"""
Unit tests for gRPC middleware components.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from common.grpc_client.constants import (
    CALC_REQ_EVENT_TYPE,
    CRITERIA_CALC_REQ_EVENT_TYPE,
    ERROR_EVENT_TYPE,
    EVENT_ACK_TYPE,
    GREET_EVENT_TYPE,
    KEEP_ALIVE_EVENT_TYPE,
)
from common.grpc_client.middleware.base import MiddlewareLink
from common.grpc_client.middleware.dispatch import DispatchMiddleware
from common.grpc_client.middleware.error import ErrorMiddleware
from common.grpc_client.middleware.logging import LoggingMiddleware
from common.grpc_client.middleware.metrics import MetricsMiddleware
from common.grpc_client.outbox import Outbox
from common.grpc_client.responses.builders import (
    AckResponseBuilder,
    ResponseBuilderRegistry,
)
from common.grpc_client.responses.spec import ResponseSpec
from common.grpc_client.router import EventRouter
from common.proto.cloudevents_pb2 import CloudEvent


class TestMiddlewareLink:
    """Test suite for MiddlewareLink base class."""

    @pytest.mark.asyncio
    async def test_handle_calls_successor(self):
        """Test that handle calls successor middleware."""
        middleware1 = MiddlewareLink()
        middleware2 = MiddlewareLink()
        middleware1.set_successor(middleware2)

        event = CloudEvent()
        event.id = "test-123"

        # Mock the successor middleware's handle
        middleware2.handle = AsyncMock(return_value=None)

        await middleware1.handle(event)

        middleware2.handle.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_handle_no_successor(self):
        """Test that handle works when there's no successor middleware."""
        middleware = MiddlewareLink()

        event = CloudEvent()
        event.id = "test-123"

        result = await middleware.handle(event)

        assert result is None

    def test_set_successor(self):
        """Test setting successor middleware."""
        middleware1 = MiddlewareLink()
        middleware2 = MiddlewareLink()

        result = middleware1.set_successor(middleware2)

        assert middleware1._successor is middleware2
        assert result is middleware2


class TestLoggingMiddleware:
    """Test suite for LoggingMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create LoggingMiddleware instance."""
        return LoggingMiddleware()

    @pytest.mark.asyncio
    async def test_handle_ack_event(self, middleware):
        """Test logging ACK event."""
        event = CloudEvent()
        event.id = "ack-123"
        event.type = EVENT_ACK_TYPE
        event.source = "test"
        event.text_data = json.dumps({"sourceEventId": "source-456", "success": True})

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_calc_request_event(self, middleware):
        """Test logging calc request event."""
        event = CloudEvent()
        event.id = "calc-123"
        event.type = CALC_REQ_EVENT_TYPE
        event.source = "test"
        event.text_data = json.dumps(
            {
                "entityId": "entity-456",
                "requestId": "req-789",
                "processorName": "TestProcessor",
            }
        )

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_request_event(self, middleware):
        """Test logging criteria calc request event."""
        event = CloudEvent()
        event.id = "criteria-123"
        event.type = CRITERIA_CALC_REQ_EVENT_TYPE
        event.source = "test"
        event.text_data = json.dumps(
            {
                "entityId": "entity-456",
                "requestId": "req-789",
                "criteriaName": "TestCriteria",
            }
        )

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_greet_event(self, middleware):
        """Test logging greet event."""
        event = CloudEvent()
        event.id = "greet-123"
        event.type = GREET_EVENT_TYPE
        event.source = "test"
        event.text_data = json.dumps({"memberId": "member-456", "success": True})

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_keep_alive_event(self, middleware):
        """Test logging keep alive event."""
        event = CloudEvent()
        event.id = "keepalive-123"
        event.type = KEEP_ALIVE_EVENT_TYPE
        event.source = "test"
        event.text_data = json.dumps({"id": "event-456"})

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_error_event(self, middleware):
        """Test logging error event."""
        event = CloudEvent()
        event.id = "error-123"
        event.type = ERROR_EVENT_TYPE
        event.source = "test"
        event.text_data = json.dumps(
            {"code": "INTERNAL_ERROR", "message": "Error occurred"}
        )

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_unknown_event(self, middleware):
        """Test logging unknown event type."""
        event = CloudEvent()
        event.id = "unknown-123"
        event.type = "UnknownEventType"
        event.source = "test"
        event.text_data = json.dumps({"data": "test"})

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self, middleware):
        """Test handling event with invalid JSON."""
        event = CloudEvent()
        event.id = "invalid-123"
        event.type = "TestEvent"
        event.source = "test"
        event.text_data = "not valid json"

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_empty_text_data(self, middleware):
        """Test handling event with empty text_data."""
        event = CloudEvent()
        event.id = "empty-123"
        event.type = "TestEvent"
        event.source = "test"
        event.text_data = ""

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_calls_successor_middleware(self, middleware):
        """Test that logging middleware calls successor in chain."""
        successor_middleware = MiddlewareLink()
        successor_middleware.handle = AsyncMock(return_value="successor_result")
        middleware.set_successor(successor_middleware)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"
        event.source = "test"
        event.text_data = json.dumps({})

        result = await middleware.handle(event)

        successor_middleware.handle.assert_called_once_with(event)
        assert result == "successor_result"


class TestDispatchMiddleware:
    """Test suite for DispatchMiddleware."""

    @pytest.fixture
    def router(self):
        """Create EventRouter instance."""
        return EventRouter()

    @pytest.fixture
    def builders(self):
        """Create ResponseBuilderRegistry instance."""
        registry = ResponseBuilderRegistry()
        registry.register(EVENT_ACK_TYPE, AckResponseBuilder())
        return registry

    @pytest.fixture
    def outbox(self):
        """Create Outbox instance."""
        return Outbox()

    @pytest.fixture
    def middleware(self, router, builders, outbox):
        """Create DispatchMiddleware instance."""
        return DispatchMiddleware(router, builders, outbox)

    @pytest.mark.asyncio
    async def test_handle_with_registered_handler(self, middleware, router, outbox):
        """Test dispatching event to registered handler."""
        # Create mock handler that returns ResponseSpec
        handler = AsyncMock(
            return_value=ResponseSpec(
                response_type=EVENT_ACK_TYPE,
                data={},
                source_event_id="source-123",
                success=True,
            )
        )
        router.register("TestEvent", handler)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"
        event.text_data = json.dumps({})

        await middleware.handle(event)

        # Verify handler was called
        handler.assert_called_once()
        # Verify response was sent to outbox
        assert not outbox._queue.empty()

    @pytest.mark.asyncio
    async def test_handle_with_unregistered_handler(self, middleware):
        """Test handling event with no registered handler."""
        event = CloudEvent()
        event.id = "test-123"
        event.type = "UnknownEvent"

        result = await middleware.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_handler_returns_none(self, middleware, router, outbox):
        """Test handling when handler returns None."""
        handler = AsyncMock(return_value=None)
        router.register("TestEvent", handler)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"

        result = await middleware.handle(event)

        handler.assert_called_once()
        # No response should be sent to outbox
        assert outbox._queue.empty()
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_with_services(self, router, builders, outbox):
        """Test dispatching with services parameter."""
        services = Mock()
        middleware = DispatchMiddleware(router, builders, outbox, services)

        handler = AsyncMock(return_value=None)
        router.register("TestEvent", handler)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"

        await middleware.handle(event)

        # Verify handler was called with services
        handler.assert_called_once_with(event, services=services)

    @pytest.mark.asyncio
    async def test_handle_keep_alive_ack_logging(self, middleware, router, outbox):
        """Test special logging for KeepAlive ACK."""
        handler = AsyncMock(
            return_value=ResponseSpec(
                response_type=EVENT_ACK_TYPE,
                data={},
                source_event_id="keepalive-456",
                success=True,
            )
        )
        router.register(KEEP_ALIVE_EVENT_TYPE, handler)

        event = CloudEvent()
        event.id = "keepalive-123"
        event.type = KEEP_ALIVE_EVENT_TYPE
        event.text_data = json.dumps({"id": "keepalive-456"})

        await middleware.handle(event)

        # Verify response was sent
        assert not outbox._queue.empty()

    @pytest.mark.asyncio
    async def test_handle_invalid_response_json(self, middleware, router, outbox):
        """Test handling when response has invalid JSON."""
        handler = AsyncMock(
            return_value=ResponseSpec(
                response_type=EVENT_ACK_TYPE, data={}, source_event_id="source-123"
            )
        )
        router.register("TestEvent", handler)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"

        await middleware.handle(event)

        # Should still send response despite logging error
        assert not outbox._queue.empty()


class TestErrorMiddleware:
    """Test suite for ErrorMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create ErrorMiddleware instance."""
        return ErrorMiddleware()

    @pytest.mark.asyncio
    async def test_handle_success(self, middleware):
        """Test handling event successfully."""
        successor_middleware = MiddlewareLink()
        successor_middleware.handle = AsyncMock(return_value=None)
        middleware.set_successor(successor_middleware)

        event = CloudEvent()
        event.id = "test-123"

        result = await middleware.handle(event)

        successor_middleware.handle.assert_called_once_with(event)
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_exception(self, middleware):
        """Test handling when successor middleware raises exception."""
        successor_middleware = MiddlewareLink()
        successor_middleware.handle = AsyncMock(side_effect=Exception("Test error"))
        middleware.set_successor(successor_middleware)

        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"

        result = await middleware.handle(event)

        # Should catch exception and return None
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_no_successor_middleware(self, middleware):
        """Test handling when there's no successor middleware."""
        event = CloudEvent()
        event.id = "test-123"

        result = await middleware.handle(event)

        assert result is None


class TestMetricsMiddleware:
    """Test suite for MetricsMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create MetricsMiddleware instance."""
        return MetricsMiddleware()

    @pytest.mark.asyncio
    async def test_handle_passes_through(self, middleware):
        """Test that metrics middleware passes through to successor."""
        successor_middleware = MiddlewareLink()
        successor_middleware.handle = AsyncMock(return_value="result")
        middleware.set_successor(successor_middleware)

        event = CloudEvent()
        event.id = "test-123"

        result = await middleware.handle(event)

        successor_middleware.handle.assert_called_once_with(event)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_handle_no_successor(self, middleware):
        """Test handling when there's no successor middleware."""
        event = CloudEvent()
        event.id = "test-123"

        result = await middleware.handle(event)

        assert result is None
