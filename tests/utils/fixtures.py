"""
Test fixtures and utilities.

This module provides pytest fixtures and utilities for testing the gRPC client
system and related components.
"""

import pytest
import asyncio
import tempfile
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from tests.utils.mocks import (
    MockServices, MockAuthService, MockRepository, MockEntityService,
    MockProcessorManager, MockEventRouter, MockGrpcClient, MockMiddleware,
    create_mock_cloud_event, create_mock_entity
)
from common.di.container import DIContainer
from common.config.manager import ConfigurationManager, Environment
from entity.cyoda_entity import CyodaEntity


@pytest.fixture
def mock_services():
    """Provide mock services for testing."""
    services = MockServices()
    yield services
    services.reset_all()


@pytest.fixture
def mock_auth_service():
    """Provide mock authentication service."""
    return MockAuthService()


@pytest.fixture
def mock_repository():
    """Provide mock repository."""
    return MockRepository()


@pytest.fixture
def mock_entity_service(mock_repository):
    """Provide mock entity service."""
    return MockEntityService(mock_repository)


@pytest.fixture
def mock_processor_manager():
    """Provide mock processor manager."""
    return MockProcessorManager()


@pytest.fixture
def mock_event_router():
    """Provide mock event router."""
    return MockEventRouter()


@pytest.fixture
def mock_grpc_client():
    """Provide mock gRPC client."""
    return MockGrpcClient()


@pytest.fixture
def mock_middleware():
    """Provide mock middleware."""
    return MockMiddleware()


@pytest.fixture
def sample_entity():
    """Provide a sample entity for testing."""
    return create_mock_entity(
        entity_id="test-entity-123",
        entity_type="test",
        name="Test Entity",
        status="active"
    )


@pytest.fixture
def sample_entities():
    """Provide multiple sample entities for testing."""
    return [
        create_mock_entity(
            entity_id=f"test-entity-{i}",
            entity_type="test",
            name=f"Test Entity {i}",
            status="active"
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_cloud_event():
    """Provide a sample CloudEvent for testing."""
    return create_mock_cloud_event(
        event_type="test.calc.request",
        event_id="test-event-123",
        source="test-source",
        data={
            "processorName": "test_processor",
            "entityId": "test-entity-123",
            "requestId": "test-request-123",
            "payload": {
                "data": {
                    "entity_id": "test-entity-123",
                    "name": "Test Entity",
                    "status": "active"
                },
                "meta": {
                    "modelKey": {
                        "name": "TestEntity"
                    }
                }
            }
        }
    )


@pytest.fixture
def sample_cloud_events():
    """Provide multiple sample CloudEvents for testing."""
    events = []
    for i in range(1, 4):
        event = create_mock_cloud_event(
            event_type="test.calc.request",
            event_id=f"test-event-{i}",
            source="test-source",
            data={
                "processorName": f"test_processor_{i}",
                "entityId": f"test-entity-{i}",
                "requestId": f"test-request-{i}",
                "payload": {
                    "data": {
                        "entity_id": f"test-entity-{i}",
                        "name": f"Test Entity {i}",
                        "status": "active"
                    },
                    "meta": {
                        "modelKey": {
                            "name": "TestEntity"
                        }
                    }
                }
            }
        )
        events.append(event)
    return events


@pytest.fixture
def di_container():
    """Provide a clean DI container for testing."""
    container = DIContainer("test")
    yield container
    # Cleanup is automatic as container goes out of scope


@pytest.fixture
def test_config_manager():
    """Provide a test configuration manager."""
    config_manager = ConfigurationManager(Environment.TESTING)
    config_manager.initialize()
    return config_manager


@pytest.fixture
def temp_config_file():
    """Provide a temporary configuration file for testing."""
    config_data = {
        "authentication": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "token_url": "https://test.example.com/oauth/token"
        },
        "grpc": {
            "address": "test.grpc.com:443",
            "timeout": 30
        },
        "repository": {
            "type": "memory"
        },
        "application": {
            "name": "Test App",
            "version": "1.0.0-test",
            "debug": True
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    Path(temp_file_path).unlink(missing_ok=True)


@pytest.fixture
def event_loop():
    """Provide an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_test_context():
    """Provide an async test context."""
    # Setup
    context = {
        "tasks": [],
        "cleanup_functions": []
    }
    
    yield context
    
    # Cleanup
    for task in context["tasks"]:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    for cleanup_func in context["cleanup_functions"]:
        try:
            if asyncio.iscoroutinefunction(cleanup_func):
                await cleanup_func()
            else:
                cleanup_func()
        except Exception as e:
            print(f"Cleanup error: {e}")


class TestDataBuilder:
    """Builder for creating test data."""
    
    @staticmethod
    def entity_data(
        entity_id: str = "test-entity",
        entity_type: str = "test",
        **kwargs
    ) -> Dict[str, Any]:
        """Build entity data for testing."""
        data = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            **kwargs
        }
        return data
    
    @staticmethod
    def cloud_event_data(
        event_type: str = "test.event",
        processor_name: str = "test_processor",
        entity_id: str = "test-entity",
        **kwargs
    ) -> Dict[str, Any]:
        """Build CloudEvent data for testing."""
        data = {
            "processorName": processor_name,
            "entityId": entity_id,
            "requestId": f"req-{entity_id}",
            "payload": {
                "data": TestDataBuilder.entity_data(entity_id=entity_id),
                "meta": {
                    "modelKey": {
                        "name": "TestEntity"
                    }
                }
            },
            **kwargs
        }
        return data
    
    @staticmethod
    def middleware_chain_config() -> Dict[str, Any]:
        """Build middleware chain configuration for testing."""
        return {
            "middlewares": [
                {
                    "type": "logging",
                    "enabled": True,
                    "priority": 10,
                    "config": {"verbose": True}
                },
                {
                    "type": "metrics",
                    "enabled": True,
                    "priority": 20,
                    "config": {"detailed_metrics": False}
                },
                {
                    "type": "error",
                    "enabled": True,
                    "priority": 30,
                    "config": {}
                },
                {
                    "type": "dispatch",
                    "enabled": True,
                    "priority": 40,
                    "config": {}
                }
            ]
        }


@pytest.fixture
def test_data_builder():
    """Provide test data builder."""
    return TestDataBuilder()


class AsyncTestHelper:
    """Helper class for async testing."""
    
    @staticmethod
    async def wait_for_condition(
        condition_func: callable,
        timeout: float = 1.0,
        interval: float = 0.1
    ) -> bool:
        """Wait for a condition to become true."""
        elapsed = 0.0
        while elapsed < timeout:
            if condition_func():
                return True
            await asyncio.sleep(interval)
            elapsed += interval
        return False
    
    @staticmethod
    async def collect_async_results(
        async_generators: List,
        max_items: int = 10,
        timeout: float = 1.0
    ) -> List[Any]:
        """Collect results from async generators."""
        results = []
        tasks = [asyncio.create_task(gen.__anext__()) for gen in async_generators]
        
        try:
            done, pending = await asyncio.wait_for(
                asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED),
                timeout=timeout
            )
            
            for task in done:
                try:
                    result = await task
                    results.append(result)
                    if len(results) >= max_items:
                        break
                except StopAsyncIteration:
                    pass
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                
        except asyncio.TimeoutError:
            for task in tasks:
                task.cancel()
        
        return results


@pytest.fixture
def async_test_helper():
    """Provide async test helper."""
    return AsyncTestHelper()


# Pytest markers for different test categories
pytest_markers = {
    "unit": pytest.mark.unit,
    "integration": pytest.mark.integration,
    "async_test": pytest.mark.asyncio,
    "slow": pytest.mark.slow,
    "network": pytest.mark.network,
    "requires_auth": pytest.mark.requires_auth,
}


def pytest_configure(config):
    """Configure pytest markers."""
    for name, marker in pytest_markers.items():
        config.addinivalue_line("markers", f"{name}: {marker.mark.name} tests")


# Custom assertions for testing
class CustomAssertions:
    """Custom assertions for testing."""
    
    @staticmethod
    def assert_entity_equal(entity1: CyodaEntity, entity2: CyodaEntity):
        """Assert that two entities are equal."""
        assert entity1.entity_id == entity2.entity_id
        assert entity1.entity_type == entity2.entity_type
        # Add more specific assertions as needed
    
    @staticmethod
    def assert_cloud_event_valid(event):
        """Assert that a CloudEvent is valid."""
        assert hasattr(event, 'type')
        assert hasattr(event, 'id')
        assert hasattr(event, 'source')
        assert event.type is not None
        assert event.id is not None
        assert event.source is not None
    
    @staticmethod
    def assert_mock_called_with_entity(mock_func, entity: CyodaEntity):
        """Assert that a mock function was called with a specific entity."""
        mock_func.assert_called()
        args, kwargs = mock_func.call_args
        if args:
            assert args[0].entity_id == entity.entity_id
        elif 'entity' in kwargs:
            assert kwargs['entity'].entity_id == entity.entity_id


@pytest.fixture
def custom_assertions():
    """Provide custom assertions."""
    return CustomAssertions()
