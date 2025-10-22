"""
Unit tests for gRPC calc and criteria_calc handlers.
"""

import json
from unittest.mock import AsyncMock, Mock

import pytest

from common.entity.cyoda_entity import CyodaEntity
from common.exception.grpc_exceptions import HandlerError, ProcessingError, ValidationError
from common.grpc_client.constants import CALC_REQ_EVENT_TYPE, CALC_RESP_EVENT_TYPE
from common.grpc_client.handlers.calc import CalcRequestHandler
from common.grpc_client.handlers.criteria_calc import CriteriaCalcRequestHandler
from common.grpc_client.responses.spec import ResponseSpec
from common.proto.cloudevents_pb2 import CloudEvent


class TestCalcRequestHandler:
    """Test suite for CalcRequestHandler."""

    @pytest.fixture
    def handler(self):
        """Create CalcRequestHandler instance."""
        return CalcRequestHandler()

    @pytest.fixture
    def processor_manager(self):
        """Create mock processor manager."""
        manager = Mock()
        manager.process_entity = AsyncMock()
        return manager

    @pytest.fixture
    def services(self, processor_manager):
        """Create mock services."""
        services = Mock()
        services.processor_manager = processor_manager
        return services

    @pytest.fixture
    def calc_event(self):
        """Create a sample calc event."""
        event = CloudEvent()
        event.id = "calc-123"
        event.type = CALC_REQ_EVENT_TYPE
        event.text_data = json.dumps({
            "processorName": "test_processor",
            "entityId": "entity-456",
            "requestId": "request-789",
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "TestEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test",
                    "value": 42
                }
            }
        })
        return event

    @pytest.mark.asyncio
    async def test_handle_calc_request_success(self, handler, services, processor_manager, calc_event):
        """Test successful calc request handling."""
        # Setup processor to return modified entity
        async def process_entity(processor_name, entity):
            entity.value = 100  # Modify the entity
            return entity

        processor_manager.process_entity = process_entity

        result = await handler.handle(calc_event, services)

        assert isinstance(result, ResponseSpec)
        assert result.response_type == CALC_RESP_EVENT_TYPE
        assert result.success is True
        assert result.data["entityId"] == "entity-456"
        assert result.data["requestId"] == "request-789"
        assert result.data["payload"]["data"]["value"] == 100

    @pytest.mark.asyncio
    async def test_handle_calc_request_with_transition(self, handler, services, processor_manager):
        """Test calc request with transition information."""
        event = CloudEvent()
        event.id = "calc-123"
        event.type = CALC_REQ_EVENT_TYPE
        event.text_data = json.dumps({
            "processorName": "test_processor",
            "entityId": "entity-456",
            "requestId": "request-789",
            "transition": {
                "name": "approve",
                "from": "draft",
                "to": "approved"
            },
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "TestEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test",
                    "value": 42
                }
            }
        })

        async def process_entity(processor_name, entity):
            # Verify transition metadata was added
            assert entity.get_metadata("current_transition") == "approve"
            return entity

        processor_manager.process_entity = process_entity

        result = await handler.handle(event, services)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_calc_request_unknown_entity_type(self, handler, services, processor_manager):
        """Test calc request with unknown entity type (fallback to CyodaEntity)."""
        event = CloudEvent()
        event.id = "calc-123"
        event.type = CALC_REQ_EVENT_TYPE
        event.text_data = json.dumps({
            "processorName": "test_processor",
            "entityId": "entity-456",
            "requestId": "request-789",
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "UnknownEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test",
                    "value": 42
                }
            }
        })

        async def process_entity(processor_name, entity):
            # Should be a CyodaEntity
            assert isinstance(entity, CyodaEntity)
            return entity

        processor_manager.process_entity = process_entity

        result = await handler.handle(event, services)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_calc_request_no_processor_manager(self, handler, calc_event):
        """Test calc request without processor manager."""
        services = Mock()
        services.processor_manager = None

        # HandlerError is wrapped in ProcessingError
        with pytest.raises(ProcessingError) as exc_info:
            await handler.handle(calc_event, services)

        assert "processor_manager not available" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_calc_request_processing_error(self, handler, services, processor_manager, calc_event):
        """Test calc request with processing error."""
        # Setup processor to raise error
        async def process_entity_error(processor_name, entity):
            raise RuntimeError("Processing failed")

        processor_manager.process_entity = process_entity_error

        with pytest.raises(ProcessingError) as exc_info:
            await handler.handle(calc_event, services)

        error = exc_info.value
        assert error.processor_name == "test_processor"
        assert error.entity_id == "entity-456"
        assert "Processing failed" in str(error)


class TestCriteriaCalcRequestHandler:
    """Test suite for CriteriaCalcRequestHandler."""

    @pytest.fixture
    def handler(self):
        """Create CriteriaCalcRequestHandler instance."""
        return CriteriaCalcRequestHandler()

    @pytest.fixture
    def processor_manager(self):
        """Create mock processor manager."""
        manager = Mock()
        manager.check_criteria = AsyncMock()
        return manager

    @pytest.fixture
    def services(self, processor_manager):
        """Create mock services."""
        services = Mock()
        services.processor_manager = processor_manager
        return services

    @pytest.fixture
    def criteria_event(self):
        """Create a sample criteria calc event."""
        event = CloudEvent()
        event.id = "criteria-123"
        event.type = "EntityCriteriaCalculationRequest"
        event.text_data = json.dumps({
            "criteriaName": "test_criteria",
            "entityId": "entity-456",
            "requestId": "request-789",
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "TestEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test",
                    "value": 42
                }
            }
        })
        return event

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_success(self, handler, services, processor_manager, criteria_event):
        """Test successful criteria calc handling."""
        # Setup processor to return True
        processor_manager.check_criteria.return_value = True

        result = await handler.handle(criteria_event, services)

        assert isinstance(result, ResponseSpec)
        assert result.success is True
        assert result.data["entityId"] == "entity-456"
        assert result.data["matches"] is True

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_with_unknown_entity(self, handler, services, processor_manager):
        """Test criteria calc with unknown entity type (fallback to CyodaEntity)."""
        event = CloudEvent()
        event.id = "criteria-123"
        event.type = "EntityCriteriaCalculationRequest"
        event.text_data = json.dumps({
            "criteriaName": "test_criteria",
            "entityId": "entity-456",
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "UnknownEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test",
                    "value": 42
                }
            }
        })

        processor_manager.check_criteria.return_value = False

        result = await handler.handle(event, services)

        assert result.success is True
        assert result.data["matches"] is False

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_with_transition(self, handler, services, processor_manager):
        """Test criteria calc with transition information."""
        event = CloudEvent()
        event.id = "criteria-123"
        event.type = "EntityCriteriaCalculationRequest"
        event.text_data = json.dumps({
            "criteriaName": "test_criteria",
            "entityId": "entity-456",
            "transition": {
                "name": "approve"
            },
            "payload": {
                "meta": {
                    "modelKey": {
                        "name": "TestEntity",
                        "version": 1
                    }
                },
                "data": {
                    "name": "Test"
                }
            }
        })

        processor_manager.check_criteria.return_value = True

        result = await handler.handle(event, services)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_no_processor_manager(self, handler, criteria_event):
        """Test criteria calc without processor manager."""
        services = Mock()
        services.processor_manager = None

        # Should handle gracefully and return response with matches=False
        result = await handler.handle(criteria_event, services)

        assert isinstance(result, ResponseSpec)
        assert result.success is True
        assert result.data["matches"] is False

    @pytest.mark.asyncio
    async def test_handle_criteria_calc_processing_error(self, handler, services, processor_manager, criteria_event):
        """Test criteria calc with processing error."""
        # Setup processor to raise error
        processor_manager.check_criteria.side_effect = ValueError("Evaluation failed")

        # Should handle gracefully and return response with matches=False
        result = await handler.handle(criteria_event, services)

        assert isinstance(result, ResponseSpec)
        assert result.success is True
        assert result.data["matches"] is False

