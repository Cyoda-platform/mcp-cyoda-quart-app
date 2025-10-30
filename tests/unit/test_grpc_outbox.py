"""
Unit tests for gRPC Outbox.
"""

import asyncio
import json
from unittest.mock import Mock, patch

import pytest

from common.grpc_client.constants import (
    CALC_RESP_EVENT_TYPE,
    CRITERIA_CALC_RESP_EVENT_TYPE,
    EVENT_ACK_TYPE,
    JOIN_EVENT_TYPE,
)
from common.grpc_client.outbox import Outbox
from common.proto.cloudevents_pb2 import CloudEvent


class TestOutbox:
    """Test suite for Outbox class."""

    @pytest.fixture
    def outbox(self):
        """Create Outbox instance."""
        return Outbox()

    @pytest.mark.asyncio
    async def test_send_event(self, outbox):
        """Test sending an event to the outbox."""
        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"

        await outbox.send(event)

        # Verify event is in queue
        assert not outbox._queue.empty()
        queued_event = await outbox._queue.get()
        assert queued_event.id == "test-123"
        assert queued_event.type == "TestEvent"

    @pytest.mark.asyncio
    async def test_close(self, outbox):
        """Test closing the outbox."""
        await outbox.close()

        # Verify sentinel (None) is in queue
        assert not outbox._queue.empty()
        sentinel = await outbox._queue.get()
        assert sentinel is None

    @pytest.mark.asyncio
    async def test_event_generator_join_event(self, outbox):
        """Test that event generator yields join event first."""
        # Close immediately to stop generator after join
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        # Should have exactly one event (join)
        assert len(events) == 1
        assert events[0].type == JOIN_EVENT_TYPE

    @pytest.mark.asyncio
    async def test_event_generator_multiple_events(self, outbox):
        """Test event generator yields multiple events."""
        # Create test events
        event1 = CloudEvent()
        event1.id = "event-1"
        event1.type = "TestEvent1"
        event1.text_data = json.dumps({"test": "data1"})

        event2 = CloudEvent()
        event2.id = "event-2"
        event2.type = "TestEvent2"
        event2.text_data = json.dumps({"test": "data2"})

        # Send events
        await outbox.send(event1)
        await outbox.send(event2)
        await outbox.close()

        # Collect events
        events = []
        async for event in outbox.event_generator():
            events.append(event)

        # Should have join + 2 events
        assert len(events) == 3
        assert events[0].type == JOIN_EVENT_TYPE
        assert events[1].id == "event-1"
        assert events[2].id == "event-2"

    @pytest.mark.asyncio
    async def test_event_generator_ack_event_logging(self, outbox):
        """Test that ACK events are logged correctly."""
        event = CloudEvent()
        event.id = "ack-123"
        event.type = EVENT_ACK_TYPE
        event.text_data = json.dumps({"sourceEventId": "source-456", "success": True})

        await outbox.send(event)
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        # Should have join + ack
        assert len(events) == 2
        assert events[1].type == EVENT_ACK_TYPE

    @pytest.mark.asyncio
    async def test_event_generator_calc_response_logging(self, outbox):
        """Test that calc response events are logged correctly."""
        event = CloudEvent()
        event.id = "calc-123"
        event.type = CALC_RESP_EVENT_TYPE
        event.text_data = json.dumps(
            {"entityId": "entity-456", "requestId": "req-789", "success": True}
        )

        await outbox.send(event)
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        assert len(events) == 2
        assert events[1].type == CALC_RESP_EVENT_TYPE

    @pytest.mark.asyncio
    async def test_event_generator_criteria_calc_response_logging(self, outbox):
        """Test that criteria calc response events are logged correctly."""
        event = CloudEvent()
        event.id = "criteria-123"
        event.type = CRITERIA_CALC_RESP_EVENT_TYPE
        event.text_data = json.dumps(
            {"entityId": "entity-456", "requestId": "req-789", "success": False}
        )

        await outbox.send(event)
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        assert len(events) == 2
        assert events[1].type == CRITERIA_CALC_RESP_EVENT_TYPE

    @pytest.mark.asyncio
    async def test_event_generator_invalid_json(self, outbox):
        """Test handling of events with invalid JSON."""
        event = CloudEvent()
        event.id = "invalid-123"
        event.type = "TestEvent"
        event.text_data = "not valid json"

        await outbox.send(event)
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        # Should still yield the event despite invalid JSON
        assert len(events) == 2
        assert events[1].id == "invalid-123"

    @pytest.mark.asyncio
    async def test_event_generator_empty_text_data(self, outbox):
        """Test handling of events with empty text_data."""
        event = CloudEvent()
        event.id = "empty-123"
        event.type = "TestEvent"
        event.text_data = ""

        await outbox.send(event)
        await outbox.close()

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        assert len(events) == 2
        assert events[1].id == "empty-123"

    @pytest.mark.asyncio
    async def test_event_generator_concurrent_sends(self, outbox):
        """Test sending events concurrently while generator is running."""

        async def send_events():
            """Send events with small delays."""
            for i in range(5):
                event = CloudEvent()
                event.id = f"event-{i}"
                event.type = "TestEvent"
                event.text_data = json.dumps({"index": i})
                await outbox.send(event)
                await asyncio.sleep(0.01)
            await outbox.close()

        # Start generator and sender concurrently
        events = []

        async def collect_events():
            async for event in outbox.event_generator():
                events.append(event)

        await asyncio.gather(collect_events(), send_events())

        # Should have join + 5 events
        assert len(events) == 6
        assert events[0].type == JOIN_EVENT_TYPE
        for i in range(5):
            assert events[i + 1].id == f"event-{i}"

    @pytest.mark.asyncio
    async def test_queue_task_done_called(self, outbox):
        """Test that task_done is called for each event."""
        event = CloudEvent()
        event.id = "test-123"
        event.type = "TestEvent"
        event.text_data = json.dumps({"test": "data"})

        await outbox.send(event)
        await outbox.close()

        # Consume events
        async for _ in outbox.event_generator():
            pass

        # Queue should be empty and all tasks done
        assert outbox._queue.empty()

    @pytest.mark.asyncio
    async def test_multiple_close_calls(self, outbox):
        """Test that multiple close calls don't cause issues."""
        await outbox.close()
        await outbox.close()
        await outbox.close()

        # Should have 3 sentinels
        assert outbox._queue.qsize() == 3

    @pytest.mark.asyncio
    async def test_event_generator_stops_on_sentinel(self, outbox):
        """Test that generator stops when it encounters sentinel."""
        event1 = CloudEvent()
        event1.id = "event-1"
        event1.type = "TestEvent"

        await outbox.send(event1)
        await outbox.close()

        # This event should not be yielded
        event2 = CloudEvent()
        event2.id = "event-2"
        event2.type = "TestEvent"
        await outbox.send(event2)

        events = []
        async for event in outbox.event_generator():
            events.append(event)

        # Should only have join + event1 (not event2)
        assert len(events) == 2
        assert events[0].type == JOIN_EVENT_TYPE
        assert events[1].id == "event-1"
