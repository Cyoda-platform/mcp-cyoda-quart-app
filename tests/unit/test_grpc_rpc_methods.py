"""
Unit tests for gRPC RPC methods.
"""

import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import grpc
import pytest

from common.grpc_client.rpc_methods import GrpcRpcMethods
from common.proto.cloudevents_pb2 import CloudEvent


class TestGrpcRpcMethods:
    """Test suite for GrpcRpcMethods class."""

    @pytest.fixture
    def auth_service(self):
        """Mock authentication service."""
        mock_auth = Mock()
        mock_auth.get_access_token_sync.return_value = "test-token-123"
        return mock_auth

    @pytest.fixture
    def rpc_methods(self, auth_service):
        """Create GrpcRpcMethods instance."""
        return GrpcRpcMethods(auth_service)

    @pytest.fixture
    def grpc_address(self):
        """Test gRPC address."""
        return "test.cyoda.com:443"

    def test_create_cloud_event(self):
        """Test CloudEvent creation."""
        event_type = "EntityStatsGetRequest"
        data = {"model": {"name": "TestEntity", "version": 1}}

        event = GrpcRpcMethods._create_cloud_event(event_type, data)

        assert event.type == event_type
        assert event.source == "python-client"
        assert event.spec_version == "1.0"
        assert event.id  # Should have a UUID

        parsed_data = json.loads(event.text_data)
        assert parsed_data == data

    def test_parse_cloud_event(self):
        """Test CloudEvent parsing."""
        event = CloudEvent()
        event.id = str(uuid.uuid4())
        event.type = "EntityStatsResponse"
        event.text_data = json.dumps({"count": 42, "modelName": "TestEntity"})

        parsed = GrpcRpcMethods._parse_cloud_event(event)

        assert parsed["count"] == 42
        assert parsed["modelName"] == "TestEntity"

    def test_parse_cloud_event_invalid_json(self):
        """Test parsing CloudEvent with invalid JSON."""
        event = CloudEvent()
        event.id = str(uuid.uuid4())
        event.text_data = "not valid json"

        parsed = GrpcRpcMethods._parse_cloud_event(event)

        assert parsed == {}

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_get_entity_stats(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test getting entity statistics via gRPC."""
        # Setup mock responses
        response1 = CloudEvent()
        response1.text_data = json.dumps(
            {"modelName": "TestEntity", "modelVersion": 1, "count": 42}
        )

        response2 = CloudEvent()
        response2.text_data = json.dumps(
            {"modelName": "OtherEntity", "modelVersion": 1, "count": 10}
        )

        mock_stub = Mock()
        mock_stub.entitySearchCollection.return_value = iter([response1, response2])
        mock_stub_class.return_value = mock_stub

        # Call method
        count = rpc_methods.get_entity_stats(grpc_address, "TestEntity", "1")

        # Verify
        assert count == 42
        mock_stub.entitySearchCollection.assert_called_once()

        # Verify request
        call_args = mock_stub.entitySearchCollection.call_args[0][0]
        assert call_args.type == "EntityStatsGetRequest"
        request_data = json.loads(call_args.text_data)
        assert request_data["model"]["name"] == "TestEntity"
        assert request_data["model"]["version"] == 1

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_get_entity_stats_with_point_in_time(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test getting entity statistics with point in time."""
        point_in_time = datetime(2024, 1, 15, 10, 30, 0)

        response = CloudEvent()
        response.text_data = json.dumps(
            {"modelName": "TestEntity", "modelVersion": 1, "count": 25}
        )

        mock_stub = Mock()
        mock_stub.entitySearchCollection.return_value = iter([response])
        mock_stub_class.return_value = mock_stub

        count = rpc_methods.get_entity_stats(
            grpc_address, "TestEntity", "1", point_in_time
        )

        assert count == 25

        # Verify pointInTime was included
        call_args = mock_stub.entitySearchCollection.call_args[0][0]
        request_data = json.loads(call_args.text_data)
        assert "pointInTime" in request_data
        assert request_data["pointInTime"] == "2024-01-15T10:30:00"

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_get_entity_stats_not_found(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test getting entity statistics when model not found."""
        response = CloudEvent()
        response.text_data = json.dumps(
            {"modelName": "OtherEntity", "modelVersion": 1, "count": 10}
        )

        mock_stub = Mock()
        mock_stub.entitySearchCollection.return_value = iter([response])
        mock_stub_class.return_value = mock_stub

        count = rpc_methods.get_entity_stats(
            grpc_address, "TestEntity", "1"  # Different model
        )

        assert count == 0  # Should return 0 when not found

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_get_entity_changes_metadata(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test getting entity change metadata via gRPC."""
        entity_id = str(uuid.uuid4())

        response1 = CloudEvent()
        response1.text_data = json.dumps(
            {
                "changeMeta": {
                    "changeId": "change-1",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "changeType": "CREATE",
                }
            }
        )

        response2 = CloudEvent()
        response2.text_data = json.dumps(
            {
                "changeMeta": {
                    "changeId": "change-2",
                    "timestamp": "2024-01-15T11:00:00Z",
                    "changeType": "UPDATE",
                }
            }
        )

        mock_stub = Mock()
        mock_stub.entitySearchCollection.return_value = iter([response1, response2])
        mock_stub_class.return_value = mock_stub

        changes = rpc_methods.get_entity_changes_metadata(grpc_address, entity_id)

        assert len(changes) == 2
        assert changes[0]["changeId"] == "change-1"
        assert changes[0]["changeType"] == "CREATE"
        assert changes[1]["changeId"] == "change-2"
        assert changes[1]["changeType"] == "UPDATE"

        # Verify request
        call_args = mock_stub.entitySearchCollection.call_args[0][0]
        assert call_args.type == "EntityChangesMetadataGetRequest"
        request_data = json.loads(call_args.text_data)
        assert request_data["entityId"] == entity_id

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_get_entity_changes_metadata_with_point_in_time(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test getting entity changes with point in time."""
        entity_id = str(uuid.uuid4())
        point_in_time = datetime(2024, 1, 15, 10, 30, 0)

        response = CloudEvent()
        response.text_data = json.dumps(
            {
                "changeMeta": {
                    "changeId": "change-1",
                    "timestamp": "2024-01-15T10:00:00Z",
                }
            }
        )

        mock_stub = Mock()
        mock_stub.entitySearchCollection.return_value = iter([response])
        mock_stub_class.return_value = mock_stub

        changes = rpc_methods.get_entity_changes_metadata(
            grpc_address, entity_id, point_in_time
        )

        assert len(changes) == 1

        # Verify pointInTime was included
        call_args = mock_stub.entitySearchCollection.call_args[0][0]
        request_data = json.loads(call_args.text_data)
        assert "pointInTime" in request_data
        assert request_data["pointInTime"] == "2024-01-15T10:30:00"

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_entity_search_collection_grpc_error(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test handling gRPC errors in entitySearchCollection."""
        mock_stub = Mock()
        mock_stub.entitySearchCollection.side_effect = grpc.RpcError(
            "Connection failed"
        )
        mock_stub_class.return_value = mock_stub

        with pytest.raises(grpc.RpcError):
            rpc_methods.entity_search_collection(
                grpc_address,
                "EntityStatsGetRequest",
                {"model": {"name": "Test", "version": 1}},
            )

    def test_close(self, rpc_methods):
        """Test closing the gRPC channel."""
        # Create a mock channel
        mock_channel = Mock()
        rpc_methods._channel = mock_channel
        rpc_methods._stub = Mock()

        rpc_methods.close()

        mock_channel.close.assert_called_once()
        assert rpc_methods._channel is None
        assert rpc_methods._stub is None

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_entity_manage(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test entityManage RPC method."""
        response = CloudEvent()
        response.text_data = json.dumps(
            {"status": "success", "entityId": "test-entity-123"}
        )

        mock_stub = Mock()
        mock_stub.entityManage.return_value = response
        mock_stub_class.return_value = mock_stub

        result = rpc_methods.entity_manage(
            grpc_address, "EntityCreateRequest", {"name": "TestEntity", "value": 42}
        )

        assert result["status"] == "success"
        assert result["entityId"] == "test-entity-123"
        mock_stub.entityManage.assert_called_once()

        # Verify request
        call_args = mock_stub.entityManage.call_args[0][0]
        assert call_args.type == "EntityCreateRequest"
        request_data = json.loads(call_args.text_data)
        assert request_data["name"] == "TestEntity"
        assert request_data["value"] == 42

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_entity_manage_grpc_error(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test entityManage with gRPC error."""
        mock_stub = Mock()
        mock_stub.entityManage.side_effect = grpc.RpcError("Connection failed")
        mock_stub_class.return_value = mock_stub

        with pytest.raises(grpc.RpcError):
            rpc_methods.entity_manage(
                grpc_address, "EntityCreateRequest", {"name": "TestEntity"}
            )

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_entity_search(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test entitySearch RPC method."""
        response = CloudEvent()
        response.text_data = json.dumps(
            {
                "entities": [
                    {"id": "1", "name": "Entity1"},
                    {"id": "2", "name": "Entity2"},
                ],
                "total": 2,
            }
        )

        mock_stub = Mock()
        mock_stub.entitySearch.return_value = response
        mock_stub_class.return_value = mock_stub

        result = rpc_methods.entity_search(
            grpc_address, "EntitySearchRequest", {"criteria": {"name": "Entity"}}
        )

        assert result["total"] == 2
        assert len(result["entities"]) == 2
        assert result["entities"][0]["name"] == "Entity1"
        mock_stub.entitySearch.assert_called_once()

        # Verify request
        call_args = mock_stub.entitySearch.call_args[0][0]
        assert call_args.type == "EntitySearchRequest"
        request_data = json.loads(call_args.text_data)
        assert request_data["criteria"]["name"] == "Entity"

    @patch("common.grpc_client.rpc_methods.grpc.secure_channel")
    @patch("common.grpc_client.rpc_methods.CloudEventsServiceStub")
    def test_entity_search_grpc_error(
        self, mock_stub_class, mock_channel, rpc_methods, grpc_address
    ):
        """Test entitySearch with gRPC error."""
        mock_stub = Mock()
        mock_stub.entitySearch.side_effect = grpc.RpcError("Search failed")
        mock_stub_class.return_value = mock_stub

        with pytest.raises(grpc.RpcError):
            rpc_methods.entity_search(
                grpc_address, "EntitySearchRequest", {"criteria": {}}
            )
