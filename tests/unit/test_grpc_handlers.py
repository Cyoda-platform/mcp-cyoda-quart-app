"""
Unit tests for gRPC handlers (ack, error, greet, keep_alive).
"""

import json
from unittest.mock import AsyncMock, Mock

import pytest

from common.grpc_client.constants import EVENT_ACK_TYPE
from common.grpc_client.handlers.ack import AckHandler
from common.grpc_client.handlers.error import ErrorHandler
from common.grpc_client.handlers.greet import GreetHandler
from common.grpc_client.handlers.keep_alive import KeepAliveHandler
from common.grpc_client.responses.spec import ResponseSpec
from common.proto.cloudevents_pb2 import CloudEvent


class TestAckHandler:
    """Test suite for AckHandler."""

    @pytest.fixture
    def handler(self):
        """Create AckHandler instance."""
        return AckHandler()

    @pytest.mark.asyncio
    async def test_handle_ack_event(self, handler):
        """Test handling ACK event."""
        event = CloudEvent()
        event.id = "ack-123"
        event.type = "EventAckResponse"
        event.text_data = json.dumps({"sourceEventId": "source-456", "success": True})

        result = await handler.handle(event)

        # Should return None (no response needed)
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_with_services(self, handler):
        """Test handling with services parameter."""
        event = CloudEvent()
        event.id = "ack-123"
        event.type = "EventAckResponse"

        services = Mock()
        result = await handler.handle(event, services)

        assert result is None


class TestErrorHandler:
    """Test suite for ErrorHandler."""

    @pytest.fixture
    def handler(self):
        """Create ErrorHandler instance."""
        return ErrorHandler()

    @pytest.mark.asyncio
    async def test_handle_error_event(self, handler):
        """Test handling error event."""
        event = CloudEvent()
        event.id = "error-123"
        event.type = "ErrorEvent"
        event.text_data = json.dumps(
            {
                "message": "Something went wrong",
                "code": "INTERNAL_ERROR",
                "sourceEventId": "source-456",
            }
        )

        result = await handler.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_error_event_missing_fields(self, handler):
        """Test handling error event with missing fields."""
        event = CloudEvent()
        event.id = "error-123"
        event.type = "ErrorEvent"
        event.text_data = json.dumps({})

        result = await handler.handle(event)

        # Should handle gracefully with defaults
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_error_event_partial_data(self, handler):
        """Test handling error event with partial data."""
        event = CloudEvent()
        event.id = "error-123"
        event.type = "ErrorEvent"
        event.text_data = json.dumps({"message": "Error occurred"})

        result = await handler.handle(event)

        assert result is None


class TestGreetHandler:
    """Test suite for GreetHandler."""

    @pytest.fixture
    def handler(self):
        """Create GreetHandler instance."""
        return GreetHandler()

    @pytest.mark.asyncio
    async def test_handle_greet_event_success(self, handler):
        """Test handling successful greet event."""
        event = CloudEvent()
        event.id = "greet-123"
        event.type = "CalculationMemberGreetEvent"
        event.text_data = json.dumps(
            {
                "memberId": "member-456",
                "joinedLegalEntityId": "CYODA",
                "success": True,
                "id": "greet-id-789",
                "warnings": [],
            }
        )

        result = await handler.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_greet_event_with_warnings(self, handler):
        """Test handling greet event with warnings."""
        event = CloudEvent()
        event.id = "greet-123"
        event.type = "CalculationMemberGreetEvent"
        event.text_data = json.dumps(
            {
                "memberId": "member-456",
                "joinedLegalEntityId": "CYODA",
                "success": True,
                "id": "greet-id-789",
                "warnings": ["Warning 1", "Warning 2"],
            }
        )

        result = await handler.handle(event)

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_greet_event_failure(self, handler):
        """Test handling failed greet event."""
        event = CloudEvent()
        event.id = "greet-123"
        event.type = "CalculationMemberGreetEvent"
        event.text_data = json.dumps(
            {
                "memberId": "member-456",
                "joinedLegalEntityId": "CYODA",
                "success": False,
                "id": "greet-id-789",
                "warnings": ["Connection failed"],
            }
        )

        result = await handler.handle(event)

        assert result is None


class TestKeepAliveHandler:
    """Test suite for KeepAliveHandler."""

    @pytest.fixture
    def handler(self):
        """Create KeepAliveHandler instance."""
        return KeepAliveHandler()

    @pytest.mark.asyncio
    async def test_handle_keep_alive_event(self, handler):
        """Test handling keep alive event."""
        event = CloudEvent()
        event.id = "keepalive-123"
        event.type = "CalculationMemberKeepAliveEvent"
        event.text_data = json.dumps(
            {"id": "event-id-456", "timestamp": "2024-01-15T10:30:00Z"}
        )

        result = await handler.handle(event)

        # Should return ResponseSpec for ACK
        assert isinstance(result, ResponseSpec)
        assert result.response_type == EVENT_ACK_TYPE
        assert result.source_event_id == "event-id-456"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_keep_alive_with_services(self, handler):
        """Test handling keep alive with services."""
        event = CloudEvent()
        event.id = "keepalive-123"
        event.type = "CalculationMemberKeepAliveEvent"
        event.text_data = json.dumps({"id": "event-id-789"})

        services = Mock()
        result = await handler.handle(event, services)

        assert isinstance(result, ResponseSpec)
        assert result.response_type == EVENT_ACK_TYPE
        assert result.source_event_id == "event-id-789"
