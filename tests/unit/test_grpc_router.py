"""
Unit tests for gRPC EventRouter.
"""

from unittest.mock import Mock

import pytest

from common.grpc_client.router import EventRouter
from common.proto.cloudevents_pb2 import CloudEvent


class TestEventRouter:
    """Test suite for EventRouter class."""

    @pytest.fixture
    def router(self):
        """Create EventRouter instance."""
        return EventRouter()

    def test_register_handler(self, router):
        """Test registering a handler for an event type."""
        handler = Mock()
        router.register("TestEvent", handler)

        assert "TestEvent" in router._handlers
        assert router._handlers["TestEvent"] is handler

    def test_register_multiple_handlers(self, router):
        """Test registering multiple handlers."""
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()

        router.register("Event1", handler1)
        router.register("Event2", handler2)
        router.register("Event3", handler3)

        assert len(router._handlers) == 3
        assert router._handlers["Event1"] is handler1
        assert router._handlers["Event2"] is handler2
        assert router._handlers["Event3"] is handler3

    def test_register_overwrites_existing_handler(self, router):
        """Test that registering same event type overwrites previous handler."""
        handler1 = Mock()
        handler2 = Mock()

        router.register("TestEvent", handler1)
        router.register("TestEvent", handler2)

        assert router._handlers["TestEvent"] is handler2
        assert router._handlers["TestEvent"] is not handler1

    def test_route_existing_event_type(self, router):
        """Test routing an event with registered handler."""
        handler = Mock()
        router.register("TestEvent", handler)

        event = CloudEvent()
        event.type = "TestEvent"

        result = router.route(event)

        assert result is handler

    def test_route_non_existing_event_type(self, router):
        """Test routing an event without registered handler."""
        event = CloudEvent()
        event.type = "UnknownEvent"

        result = router.route(event)

        assert result is None

    def test_route_empty_router(self, router):
        """Test routing when no handlers are registered."""
        event = CloudEvent()
        event.type = "TestEvent"

        result = router.route(event)

        assert result is None

    def test_route_case_sensitive(self, router):
        """Test that event type routing is case-sensitive."""
        handler = Mock()
        router.register("TestEvent", handler)

        event1 = CloudEvent()
        event1.type = "TestEvent"

        event2 = CloudEvent()
        event2.type = "testevent"

        event3 = CloudEvent()
        event3.type = "TESTEVENT"

        assert router.route(event1) is handler
        assert router.route(event2) is None
        assert router.route(event3) is None

    def test_route_with_different_event_types(self, router):
        """Test routing different event types to different handlers."""
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()

        router.register("calc.request", handler1)
        router.register("calc.response", handler2)
        router.register("criteria.calc.request", handler3)

        event1 = CloudEvent()
        event1.type = "calc.request"

        event2 = CloudEvent()
        event2.type = "calc.response"

        event3 = CloudEvent()
        event3.type = "criteria.calc.request"

        assert router.route(event1) is handler1
        assert router.route(event2) is handler2
        assert router.route(event3) is handler3

    def test_handlers_dict_initially_empty(self, router):
        """Test that handlers dict is initially empty."""
        assert len(router._handlers) == 0
        assert router._handlers == {}

    def test_register_none_handler(self, router):
        """Test registering None as a handler."""
        router.register("TestEvent", None)

        assert router._handlers["TestEvent"] is None

        event = CloudEvent()
        event.type = "TestEvent"

        assert router.route(event) is None

    def test_register_callable_handler(self, router):
        """Test registering a callable as handler."""

        def my_handler():
            return "handled"

        router.register("TestEvent", my_handler)

        event = CloudEvent()
        event.type = "TestEvent"

        result = router.route(event)
        assert result is my_handler
        assert result() == "handled"

    def test_register_class_instance_handler(self, router):
        """Test registering a class instance as handler."""

        class MyHandler:
            def handle(self):
                return "handled"

        handler_instance = MyHandler()
        router.register("TestEvent", handler_instance)

        event = CloudEvent()
        event.type = "TestEvent"

        result = router.route(event)
        assert result is handler_instance
        assert result.handle() == "handled"

