"""
Helper methods for calling gRPC RPC methods (non-streaming).

This module provides convenient wrappers for calling the various RPC methods
defined in the CloudEventsService, including temporal query support.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import grpc

from common.proto.cloudevents_pb2 import CloudEvent
from common.proto.cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub

logger = logging.getLogger(__name__)


class GrpcRpcMethods:
    """
    Helper class for calling gRPC RPC methods.

    Provides methods for:
    - Entity management (create, update, delete, transition)
    - Entity search (get, search, stats, changes)
    - Model management
    """

    def __init__(self, auth_service: Any):
        """
        Initialize with authentication service.

        Args:
            auth_service: Service providing get_access_token_sync() method
        """
        self.auth_service = auth_service
        self._channel: Optional[grpc.Channel] = None
        self._stub: Optional[CloudEventsServiceStub] = None

    def _get_stub(self, grpc_address: str) -> CloudEventsServiceStub:
        """Get or create gRPC stub."""
        if self._stub is None:
            # Create credentials
            call_creds = grpc.metadata_call_credentials(
                lambda context, callback: callback(
                    [
                        (
                            "authorization",
                            f"Bearer {self.auth_service.get_access_token_sync()}",
                        )
                    ],
                    None,
                )
            )
            ssl_creds = grpc.ssl_channel_credentials()
            creds = grpc.composite_channel_credentials(ssl_creds, call_creds)

            # Create channel
            self._channel = grpc.secure_channel(grpc_address, creds)
            self._stub = CloudEventsServiceStub(self._channel)  # type: ignore[no-untyped-call]

        return self._stub

    def close(self) -> None:
        """Close the gRPC channel."""
        if self._channel:
            self._channel.close()
            self._channel = None
            self._stub = None

    @staticmethod
    def _create_cloud_event(event_type: str, data: Dict[str, Any]) -> CloudEvent:
        """
        Create a CloudEvent from event type and data.

        Args:
            event_type: Type of the event (e.g., "EntityStatsGetRequest")
            data: Event data as dictionary

        Returns:
            CloudEvent protobuf message
        """
        event = CloudEvent()
        event.id = str(uuid.uuid4())
        event.type = event_type
        event.source = "python-client"
        event.spec_version = "1.0"
        event.text_data = json.dumps(data)
        return event

    @staticmethod
    def _parse_cloud_event(event: CloudEvent) -> Dict[str, Any]:
        """
        Parse CloudEvent to dictionary.

        Args:
            event: CloudEvent protobuf message

        Returns:
            Parsed event data
        """
        try:
            return json.loads(event.text_data)
        except (json.JSONDecodeError, AttributeError):
            return {}

    def entity_search_collection(
        self, grpc_address: str, request_type: str, request_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Call entitySearchCollection RPC method.

        This is a server-streaming RPC that returns multiple responses.

        Args:
            grpc_address: gRPC server address
            request_type: Type of request (e.g., "EntityStatsGetRequest")
            request_data: Request data dictionary

        Returns:
            List of response dictionaries
        """
        stub = self._get_stub(grpc_address)
        request_event = self._create_cloud_event(request_type, request_data)

        try:
            responses = []
            for response_event in stub.entitySearchCollection(request_event):
                response_data = self._parse_cloud_event(response_event)
                responses.append(response_data)
            return responses
        except grpc.RpcError as e:
            logger.error(f"gRPC error in entitySearchCollection: {e}")
            raise

    def get_entity_stats(
        self,
        grpc_address: str,
        model_name: str,
        model_version: str,
        point_in_time: Optional[datetime] = None,
    ) -> int:
        """
        Get entity count statistics.

        Args:
            grpc_address: gRPC server address
            model_name: Entity model name
            model_version: Entity model version
            point_in_time: Optional point in time for historical stats

        Returns:
            Entity count
        """
        request_data = {
            "id": str(uuid.uuid4()),
            "model": {"name": model_name, "version": int(model_version)},
        }

        if point_in_time:
            request_data["pointInTime"] = point_in_time.isoformat()

        responses = self.entity_search_collection(
            grpc_address, "EntityStatsGetRequest", request_data
        )

        # Find matching model in responses
        for response in responses:
            if response.get("modelName") == model_name and str(
                response.get("modelVersion")
            ) == str(model_version):
                return response.get("count", 0)

        return 0

    def get_entity_changes_metadata(
        self,
        grpc_address: str,
        entity_id: str,
        point_in_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get entity change history metadata.

        Args:
            grpc_address: gRPC server address
            entity_id: Entity technical ID
            point_in_time: Optional point in time to get changes up to

        Returns:
            List of change metadata dictionaries
        """
        request_data = {"id": str(uuid.uuid4()), "entityId": entity_id}

        if point_in_time:
            request_data["pointInTime"] = point_in_time.isoformat()

        responses = self.entity_search_collection(
            grpc_address, "EntityChangesMetadataGetRequest", request_data
        )

        # Extract changeMeta from each response
        changes = []
        for response in responses:
            if "changeMeta" in response:
                changes.append(response["changeMeta"])

        return changes

    def entity_manage(
        self, grpc_address: str, request_type: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call entityManage RPC method (unary).

        Args:
            grpc_address: gRPC server address
            request_type: Type of request
            request_data: Request data dictionary

        Returns:
            Response dictionary
        """
        stub = self._get_stub(grpc_address)
        request_event = self._create_cloud_event(request_type, request_data)

        try:
            response_event = stub.entityManage(request_event)
            return self._parse_cloud_event(response_event)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in entityManage: {e}")
            raise

    def entity_search(
        self, grpc_address: str, request_type: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call entitySearch RPC method (unary).

        Args:
            grpc_address: gRPC server address
            request_type: Type of request
            request_data: Request data dictionary

        Returns:
            Response dictionary
        """
        stub = self._get_stub(grpc_address)
        request_event = self._create_cloud_event(request_type, request_data)

        try:
            response_event = stub.entitySearch(request_event)
            return self._parse_cloud_event(response_event)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in entitySearch: {e}")
            raise
