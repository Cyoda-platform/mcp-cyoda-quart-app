"""
Unit tests for gRPC response builders.
"""

import json

import pytest

from common.grpc_client.constants import (
    CALC_RESP_EVENT_TYPE,
    CRITERIA_CALC_RESP_EVENT_TYPE,
    EVENT_ACK_TYPE,
    JOIN_EVENT_TYPE,
    OWNER,
    SOURCE,
    SPEC_VERSION,
    TAGS,
)
from common.grpc_client.responses.builders import (
    AckResponseBuilder,
    CalcResponseBuilder,
    CriteriaCalcResponseBuilder,
    JoinResponseBuilder,
    ResponseBuilder,
    ResponseBuilderRegistry,
)
from common.grpc_client.responses.spec import ResponseSpec


class TestResponseBuilder:
    """Test suite for ResponseBuilder base class."""

    def test_build_not_implemented(self):
        """Test that base class build raises NotImplementedError."""
        builder = ResponseBuilder()
        spec = ResponseSpec(response_type="test", data={})

        with pytest.raises(NotImplementedError):
            builder.build(spec)


class TestResponseBuilderRegistry:
    """Test suite for ResponseBuilderRegistry."""

    @pytest.fixture
    def registry(self):
        """Create ResponseBuilderRegistry instance."""
        return ResponseBuilderRegistry()

    def test_register_builder(self, registry):
        """Test registering a builder."""
        builder = AckResponseBuilder()
        registry.register(EVENT_ACK_TYPE, builder)

        assert EVENT_ACK_TYPE in registry._builders
        assert registry._builders[EVENT_ACK_TYPE] is builder

    def test_get_registered_builder(self, registry):
        """Test getting a registered builder."""
        builder = AckResponseBuilder()
        registry.register(EVENT_ACK_TYPE, builder)

        result = registry.get(EVENT_ACK_TYPE)

        assert result is builder

    def test_get_unregistered_builder_raises_error(self, registry):
        """Test getting unregistered builder raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            registry.get("UnknownType")

        assert "No builder registered for response_type: UnknownType" in str(
            exc_info.value
        )

    def test_register_multiple_builders(self, registry):
        """Test registering multiple builders."""
        ack_builder = AckResponseBuilder()
        join_builder = JoinResponseBuilder()
        calc_builder = CalcResponseBuilder()

        registry.register(EVENT_ACK_TYPE, ack_builder)
        registry.register(JOIN_EVENT_TYPE, join_builder)
        registry.register(CALC_RESP_EVENT_TYPE, calc_builder)

        assert len(registry._builders) == 3
        assert registry.get(EVENT_ACK_TYPE) is ack_builder
        assert registry.get(JOIN_EVENT_TYPE) is join_builder
        assert registry.get(CALC_RESP_EVENT_TYPE) is calc_builder

    def test_register_overwrites_existing(self, registry):
        """Test that registering same type overwrites previous builder."""
        builder1 = AckResponseBuilder()
        builder2 = AckResponseBuilder()

        registry.register(EVENT_ACK_TYPE, builder1)
        registry.register(EVENT_ACK_TYPE, builder2)

        assert registry.get(EVENT_ACK_TYPE) is builder2
        assert registry.get(EVENT_ACK_TYPE) is not builder1


class TestAckResponseBuilder:
    """Test suite for AckResponseBuilder."""

    @pytest.fixture
    def builder(self):
        """Create AckResponseBuilder instance."""
        return AckResponseBuilder()

    def test_build_ack_response(self, builder):
        """Test building ACK response."""
        spec = ResponseSpec(
            response_type=EVENT_ACK_TYPE,
            data={},
            source_event_id="source-123",
            success=True,
        )

        event = builder.build(spec)

        assert event.type == EVENT_ACK_TYPE
        assert event.source == SOURCE
        assert event.spec_version == SPEC_VERSION
        assert event.id  # Should have UUID

        data = json.loads(event.text_data)
        assert data["sourceEventId"] == "source-123"
        assert data["owner"] == OWNER
        assert data["success"] is True

    def test_build_ack_response_has_unique_id(self, builder):
        """Test that each ACK response has unique ID."""
        spec = ResponseSpec(
            response_type=EVENT_ACK_TYPE, data={}, source_event_id="source-123"
        )

        event1 = builder.build(spec)
        event2 = builder.build(spec)

        assert event1.id != event2.id


class TestJoinResponseBuilder:
    """Test suite for JoinResponseBuilder."""

    @pytest.fixture
    def builder(self):
        """Create JoinResponseBuilder instance."""
        return JoinResponseBuilder()

    def test_build_join_response(self, builder):
        """Test building JOIN response."""
        spec = ResponseSpec(response_type=JOIN_EVENT_TYPE, data={})

        event = builder.build(spec)

        assert event.type == JOIN_EVENT_TYPE
        assert event.source == SOURCE
        assert event.spec_version == SPEC_VERSION
        assert event.id  # Should have UUID

        data = json.loads(event.text_data)
        assert data["owner"] == OWNER
        assert data["tags"] == TAGS

    def test_build_join_response_has_unique_id(self, builder):
        """Test that each JOIN response has unique ID."""
        spec = ResponseSpec(response_type=JOIN_EVENT_TYPE, data={})

        event1 = builder.build(spec)
        event2 = builder.build(spec)

        assert event1.id != event2.id


class TestCalcResponseBuilder:
    """Test suite for CalcResponseBuilder."""

    @pytest.fixture
    def builder(self):
        """Create CalcResponseBuilder instance."""
        return CalcResponseBuilder()

    def test_build_calc_response(self, builder):
        """Test building calc response."""
        spec = ResponseSpec(
            response_type=CALC_RESP_EVENT_TYPE,
            data={
                "requestId": "req-123",
                "entityId": "entity-456",
                "payload": {"result": "calculated"},
            },
        )

        event = builder.build(spec)

        assert event.type == CALC_RESP_EVENT_TYPE
        assert event.source == SOURCE
        assert event.spec_version == SPEC_VERSION
        assert event.id  # Should have UUID

        data = json.loads(event.text_data)
        assert data["requestId"] == "req-123"
        assert data["entityId"] == "entity-456"
        assert data["owner"] == OWNER
        assert data["payload"] == {"result": "calculated"}
        assert data["success"] is True

    def test_build_calc_response_with_empty_payload(self, builder):
        """Test building calc response with empty payload."""
        spec = ResponseSpec(
            response_type=CALC_RESP_EVENT_TYPE,
            data={"requestId": "req-123", "entityId": "entity-456", "payload": None},
        )

        event = builder.build(spec)

        data = json.loads(event.text_data)
        assert data["payload"] is None

    def test_build_calc_response_missing_fields(self, builder):
        """Test building calc response with missing fields."""
        spec = ResponseSpec(response_type=CALC_RESP_EVENT_TYPE, data={})

        event = builder.build(spec)

        data = json.loads(event.text_data)
        assert data["requestId"] is None
        assert data["entityId"] is None
        assert data["payload"] is None


class TestCriteriaCalcResponseBuilder:
    """Test suite for CriteriaCalcResponseBuilder."""

    @pytest.fixture
    def builder(self):
        """Create CriteriaCalcResponseBuilder instance."""
        return CriteriaCalcResponseBuilder()

    def test_build_criteria_calc_response(self, builder):
        """Test building criteria calc response."""
        spec = ResponseSpec(
            response_type=CRITERIA_CALC_RESP_EVENT_TYPE,
            data={
                "requestId": "req-123",
                "entityId": "entity-456",
                "matches": True,
            },
        )

        event = builder.build(spec)

        assert event.type == CRITERIA_CALC_RESP_EVENT_TYPE
        assert event.source == SOURCE
        assert event.spec_version == SPEC_VERSION
        assert event.id  # Should have UUID

        data = json.loads(event.text_data)
        assert data["requestId"] == "req-123"
        assert data["entityId"] == "entity-456"
        assert data["owner"] == OWNER
        assert data["matches"] is True
        assert data["success"] is True

    def test_build_criteria_calc_response_no_match(self, builder):
        """Test building criteria calc response with no match."""
        spec = ResponseSpec(
            response_type=CRITERIA_CALC_RESP_EVENT_TYPE,
            data={
                "requestId": "req-123",
                "entityId": "entity-456",
                "matches": False,
            },
        )

        event = builder.build(spec)

        data = json.loads(event.text_data)
        assert data["matches"] is False

    def test_build_criteria_calc_response_missing_fields(self, builder):
        """Test building criteria calc response with missing fields."""
        spec = ResponseSpec(response_type=CRITERIA_CALC_RESP_EVENT_TYPE, data={})

        event = builder.build(spec)

        data = json.loads(event.text_data)
        assert data["requestId"] is None
        assert data["entityId"] is None
        assert data["matches"] is None

