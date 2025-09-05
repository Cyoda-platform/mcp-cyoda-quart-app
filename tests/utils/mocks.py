"""
Mock utilities for testing.

This module provides comprehensive mock objects and utilities for testing
the gRPC client system and related components.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Callable
from unittest.mock import Mock, AsyncMock, MagicMock
from dataclasses import dataclass

from proto.cloudevents_pb2 import CloudEvent
from entity.cyoda_entity import CyodaEntity
from common.interfaces.services import (
    IAuthService, IProcessorManager,
    IGrpcClient, IEventRouter, IResponseBuilder, IMiddleware
)
from common.repository.crud_repository import CrudRepository
from common.service.entity_service import EntityService


@dataclass
class MockEventData:
    """Mock event data for testing."""
    event_type: str
    event_id: str
    source: str
    data: Dict[str, Any]


class MockAuthService(IAuthService):
    """Mock authentication service for testing."""
    
    def __init__(self, token: str = "mock_token"):
        self.token = token
        self.token_calls = 0
        self.invalidate_calls = 0
    
    def get_access_token_sync(self) -> str:
        """Get access token synchronously."""
        self.token_calls += 1
        return self.token
    
    async def get_access_token(self) -> str:
        """Get access token asynchronously."""
        self.token_calls += 1
        return self.token
    
    def invalidate_token(self) -> None:
        """Invalidate current token."""
        self.invalidate_calls += 1


class MockRepository(CrudRepository):
    """Mock repository for testing."""
    
    def __init__(self):
        self.entities: Dict[str, CyodaEntity] = {}
        self.save_calls = 0
        self.find_calls = 0
        self.delete_calls = 0
    
    async def save(self, entity: CyodaEntity) -> CyodaEntity:
        """Save an entity."""
        self.save_calls += 1
        self.entities[entity.entity_id] = entity
        return entity
    
    async def find_by_id(self, entity_id: str) -> Optional[CyodaEntity]:
        """Find entity by ID."""
        self.find_calls += 1
        return self.entities.get(entity_id)
    
    async def find_all(self) -> List[CyodaEntity]:
        """Find all entities."""
        self.find_calls += 1
        return list(self.entities.values())
    
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        self.delete_calls += 1
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False


class MockEntityService(EntityService):
    """Mock entity service for testing."""
    
    def __init__(self, repository: Optional[MockRepository] = None):
        self.repository = repository or MockRepository()
        self.create_calls = 0
        self.get_calls = 0
        self.update_calls = 0
        self.delete_calls = 0
        self.list_calls = 0
    
    async def create_entity(self, entity_data: Dict[str, Any]) -> CyodaEntity:
        """Create a new entity."""
        self.create_calls += 1
        entity = CyodaEntity(**entity_data)
        await self.repository.save(entity)
        return entity
    
    async def get_entity(self, entity_id: str) -> Optional[CyodaEntity]:
        """Get entity by ID."""
        self.get_calls += 1
        return await self.repository.find_by_id(entity_id)
    
    async def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> CyodaEntity:
        """Update an entity."""
        self.update_calls += 1
        entity = await self.repository.find_by_id(entity_id)
        if entity:
            for key, value in updates.items():
                setattr(entity, key, value)
            await self.repository.save(entity)
        return entity
    
    async def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        self.delete_calls += 1
        return await self.repository.delete(entity_id)
    
    async def list_entities(self) -> List[CyodaEntity]:
        """List all entities."""
        self.list_calls += 1
        return await self.repository.find_all()


class MockProcessorManager(IProcessorManager):
    """Mock processor manager for testing."""
    
    def __init__(self):
        self.processors: Dict[str, Callable] = {}
        self.criteria: Dict[str, Callable] = {}
        self.process_calls = 0
        self.criteria_calls = 0
    
    def add_processor(self, name: str, processor_func: Callable):
        """Add a mock processor."""
        self.processors[name] = processor_func
    
    def add_criteria(self, name: str, criteria_func: Callable):
        """Add a mock criteria checker."""
        self.criteria[name] = criteria_func
    
    async def process_entity(self, processor_name: str, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process an entity using the specified processor."""
        self.process_calls += 1
        if processor_name in self.processors:
            return await self.processors[processor_name](entity, **kwargs)
        else:
            # Default behavior: just return the entity
            return entity
    
    async def check_criteria(self, criteria_name: str, entity: CyodaEntity, **kwargs) -> bool:
        """Check if entity meets the specified criteria."""
        self.criteria_calls += 1
        if criteria_name in self.criteria:
            return await self.criteria[criteria_name](entity, **kwargs)
        else:
            # Default behavior: return True
            return True
    
    def list_processors(self) -> List[str]:
        """List available processors."""
        return list(self.processors.keys())
    
    def list_criteria(self) -> List[str]:
        """List available criteria."""
        return list(self.criteria.keys())
    
    def get_processor_info(self, processor_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a processor."""
        if processor_name in self.processors:
            return {
                "name": processor_name,
                "type": "mock_processor",
                "description": f"Mock processor: {processor_name}"
            }
        return None


class MockEventRouter(IEventRouter):
    """Mock event router for testing."""
    
    def __init__(self):
        self.handlers: Dict[str, Any] = {}
        self.register_calls = 0
        self.route_calls = 0
    
    def register(self, event_type: str, handler: Any) -> None:
        """Register an event handler."""
        self.register_calls += 1
        self.handlers[event_type] = handler
    
    def route(self, event: Any) -> Optional[Any]:
        """Route an event to its handler."""
        self.route_calls += 1
        if hasattr(event, 'type') and event.type in self.handlers:
            return self.handlers[event.type]
        return None


class MockMiddleware(IMiddleware):
    """Mock middleware for testing."""
    
    def __init__(self, name: str = "mock_middleware"):
        self.name = name
        self.handle_calls = 0
        self.successor: Optional[IMiddleware] = None
        self.should_call_successor = True
        self.return_value = None
    
    async def handle(self, event: Any) -> Any:
        """Handle an event."""
        self.handle_calls += 1
        
        if self.should_call_successor and self.successor:
            return await self.successor.handle(event)
        
        return self.return_value
    
    def set_successor(self, successor: IMiddleware) -> IMiddleware:
        """Set the next middleware in the chain."""
        self.successor = successor
        return successor


class MockGrpcClient(IGrpcClient):
    """Mock gRPC client for testing."""
    
    def __init__(self):
        self.stream_calls = 0
        self.stop_calls = 0
        self.is_running = False
        self.events_to_send: List[MockEventData] = []
        self.event_handler: Optional[Callable] = None
    
    def add_event(self, event_data: MockEventData):
        """Add an event to be sent during streaming."""
        self.events_to_send.append(event_data)
    
    def set_event_handler(self, handler: Callable):
        """Set the event handler for processing events."""
        self.event_handler = handler
    
    async def grpc_stream(self) -> None:
        """Start the gRPC streaming connection."""
        self.stream_calls += 1
        self.is_running = True
        
        # Send mock events if handler is set
        if self.event_handler:
            for event_data in self.events_to_send:
                mock_event = self._create_mock_cloud_event(event_data)
                await self.event_handler(mock_event)
    
    def stop(self) -> None:
        """Stop the gRPC client."""
        self.stop_calls += 1
        self.is_running = False
    
    def _create_mock_cloud_event(self, event_data: MockEventData) -> CloudEvent:
        """Create a mock CloudEvent."""
        event = CloudEvent()
        event.type = event_data.event_type
        event.id = event_data.event_id
        event.source = event_data.source
        event.text_data = json.dumps(event_data.data)
        return event


class MockServices:
    """Mock services container for testing."""
    
    def __init__(self):
        self.auth_service = MockAuthService()
        self.repository = MockRepository()
        self.entity_service = MockEntityService(self.repository)
        self.processor_manager = MockProcessorManager()
        self.event_router = MockEventRouter()
        self.grpc_client = MockGrpcClient()
        self.processor_loop = Mock()
    
    def reset_all(self):
        """Reset all mock services to initial state."""
        self.auth_service = MockAuthService()
        self.repository = MockRepository()
        self.entity_service = MockEntityService(self.repository)
        self.processor_manager = MockProcessorManager()
        self.event_router = MockEventRouter()
        self.grpc_client = MockGrpcClient()
        self.processor_loop = Mock()


def create_mock_cloud_event(
    event_type: str = "test.event",
    event_id: str = "test-id",
    source: str = "test-source",
    data: Optional[Dict[str, Any]] = None
) -> CloudEvent:
    """Create a mock CloudEvent for testing."""
    event = CloudEvent()
    event.type = event_type
    event.id = event_id
    event.source = source
    event.text_data = json.dumps(data or {})
    return event


def create_mock_entity(
    entity_id: str = "test-entity",
    entity_type: str = "test",
    **kwargs
) -> CyodaEntity:
    """Create a mock CyodaEntity for testing."""
    data = {
        "entity_id": entity_id,
        "entity_type": entity_type,
        **kwargs
    }
    return CyodaEntity(**data)


async def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return await coro
    finally:
        loop.close()


class AsyncContextManagerMock:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.enter_calls = 0
        self.exit_calls = 0
    
    async def __aenter__(self):
        self.enter_calls += 1
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exit_calls += 1
        return False


def create_mock_response(status_code: int = 200, json_data: Optional[Dict] = None):
    """Create a mock HTTP response."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


# Global mock services instance for easy access in tests
mock_services = MockServices()
