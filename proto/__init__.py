"""
Protocol buffer definitions and generated code.

This package contains:
- Protocol buffer definitions (.proto files)
- Generated Python code from protobuf compiler
- gRPC service stubs and client code
"""

# Import the main gRPC components for easy access
from .cloudevents_pb2 import CloudEvent
from .cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub

__all__ = [
    'CloudEvent',
    'CloudEventsServiceStub',
]
