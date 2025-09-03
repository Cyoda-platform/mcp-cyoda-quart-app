"""
Test cases for gRPC handlers.

This module demonstrates the testing infrastructure and provides comprehensive
tests for the gRPC handler system.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from common.grpc_client.handlers.calc import CalcRequestHandler
from common.grpc_client.handlers.criteria_calc import CriteriaCalcRequestHandler
from common.grpc_client.handlers.greet import GreetHandler
from common.grpc_client.handlers.error import ErrorHandler
from common.grpc_client.constants import CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE
from common.exception.grpc_exceptions import ProcessingError, HandlerError
from tests.utils.mocks import MockServices, create_mock_cloud_event, create_mock_entity
from tests.utils.fixtures import TestDataBuilder


class TestCalcRequestHandler:
    """Test cases for CalcRequestHandler."""
    
    @pytest.fixture
    def handler(self):
        """Provide CalcRequestHandler instance."""
        return CalcRequestHandler()
    
    @pytest.fixture
    def mock_services(self):
        """Provide mock services."""
        services = MockServices()
        # Add a test processor
        async def test_processor(entity, **kwargs):
            entity.add_metadata("processed", True)
            entity.add_metadata("processor", "test_processor")
            return entity
        
        services.processor_manager.add_processor("test_processor", test_processor)
        return services
    
    @pytest.fixture
    def sample_event(self):
        """Provide sample calc request event."""
        data = TestDataBuilder.cloud_event_data(
            processor_name="test_processor",
            entity_id="test-entity-123"
        )
        return create_mock_cloud_event(
            event_type=CALC_REQ_EVENT_TYPE,
            event_id="calc-event-123",
            data=data
        )
    
    @pytest.mark.asyncio
    async def test_successful_processing(self, handler, mock_services, sample_event):
        """Test successful entity processing."""
        # Act
        result = await handler.handle(sample_event, mock_services)
        
        # Assert
        assert result is not None
        assert result.response_type == "calc.response"
        assert mock_services.processor_manager.process_calls == 1
        
        # Check that entity was processed
        response_data = result.data
        assert response_data["entityId"] == "test-entity-123"
        assert response_data["payload"]["data"]["metadata"]["processed"] is True
    
    @pytest.mark.asyncio
    async def test_missing_processor_manager(self, handler, sample_event):
        """Test handling when processor manager is missing."""
        # Arrange
        services = Mock()
        services.processor_manager = None
        
        # Act & Assert
        with pytest.raises(HandlerError) as exc_info:
            await handler.handle(sample_event, services)
        
        assert "processor_manager not available" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_processor_failure(self, handler, mock_services, sample_event):
        """Test handling of processor failures."""
        # Arrange
        async def failing_processor(entity, **kwargs):
            raise ValueError("Processor failed")
        
        mock_services.processor_manager.add_processor("test_processor", failing_processor)
        
        # Act & Assert
        with pytest.raises(ProcessingError) as exc_info:
            await handler.handle(sample_event, services=mock_services)
        
        assert "test_processor" in str(exc_info.value)
        assert "test-entity-123" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_entity_type(self, handler, mock_services):
        """Test handling of invalid entity types."""
        # Arrange
        data = TestDataBuilder.cloud_event_data(
            processor_name="test_processor",
            entity_id="test-entity-123"
        )
        # Set invalid entity type
        data["payload"]["meta"]["modelKey"]["name"] = "InvalidEntity"
        
        event = create_mock_cloud_event(
            event_type=CALC_REQ_EVENT_TYPE,
            data=data
        )
        
        # Act
        result = await handler.handle(event, mock_services)
        
        # Assert - should fallback to generic entity
        assert result is not None
        assert mock_services.processor_manager.process_calls == 1


class TestCriteriaCalcRequestHandler:
    """Test cases for CriteriaCalcRequestHandler."""
    
    @pytest.fixture
    def handler(self):
        """Provide CriteriaCalcRequestHandler instance."""
        return CriteriaCalcRequestHandler()
    
    @pytest.fixture
    def mock_services(self):
        """Provide mock services with criteria."""
        services = MockServices()
        # Add a test criteria
        async def test_criteria(entity, **kwargs):
            return entity.get_metadata("status") == "active"
        
        services.processor_manager.add_criteria("test_criteria", test_criteria)
        return services
    
    @pytest.fixture
    def sample_event(self):
        """Provide sample criteria calc request event."""
        data = TestDataBuilder.cloud_event_data(
            entity_id="test-entity-123"
        )
        data["criteriaName"] = "test_criteria"
        del data["processorName"]  # Criteria events don't have processor name
        
        return create_mock_cloud_event(
            event_type=CRITERIA_CALC_REQ_EVENT_TYPE,
            event_id="criteria-event-123",
            data=data
        )
    
    @pytest.mark.asyncio
    async def test_successful_criteria_check(self, handler, mock_services, sample_event):
        """Test successful criteria checking."""
        # Act
        result = await handler.handle(sample_event, mock_services)
        
        # Assert
        assert result is not None
        assert result.response_type == "criteria_calc.response"
        assert mock_services.processor_manager.criteria_calls == 1
        
        # Check response data
        response_data = result.data
        assert response_data["entityId"] == "test-entity-123"
        assert "matches" in response_data
    
    @pytest.mark.asyncio
    async def test_criteria_returns_false(self, handler, mock_services, sample_event):
        """Test criteria that returns false."""
        # Arrange - add criteria that returns false
        async def false_criteria(entity, **kwargs):
            return False
        
        mock_services.processor_manager.add_criteria("test_criteria", false_criteria)
        
        # Act
        result = await handler.handle(sample_event, mock_services)
        
        # Assert
        assert result is not None
        response_data = result.data
        assert response_data["matches"] is False


class TestGreetHandler:
    """Test cases for GreetHandler."""
    
    @pytest.fixture
    def handler(self):
        """Provide GreetHandler instance."""
        return GreetHandler()
    
    @pytest.fixture
    def sample_event(self):
        """Provide sample greet event."""
        return create_mock_cloud_event(
            event_type="greet",
            event_id="greet-event-123",
            data={"message": "Hello, World!"}
        )
    
    @pytest.mark.asyncio
    async def test_greet_handling(self, handler, sample_event):
        """Test basic greet event handling."""
        # Act
        result = await handler.handle(sample_event)
        
        # Assert
        assert result is None  # Greet handler returns None
    
    @pytest.mark.asyncio
    async def test_greet_with_services(self, handler, sample_event):
        """Test greet handling with services."""
        # Arrange
        services = Mock()
        services.chat_service = Mock()
        services.processor_loop = Mock()
        services.processor_loop.run_coroutine = Mock()
        
        # Act
        result = await handler.handle(sample_event, services)
        
        # Assert
        assert result is None
        services.processor_loop.run_coroutine.assert_called_once()


class TestErrorHandler:
    """Test cases for ErrorHandler."""
    
    @pytest.fixture
    def handler(self):
        """Provide ErrorHandler instance."""
        return ErrorHandler()
    
    @pytest.fixture
    def sample_event(self):
        """Provide sample error event."""
        return create_mock_cloud_event(
            event_type="error",
            event_id="error-event-123",
            data={
                "message": "Something went wrong",
                "code": "PROCESSING_ERROR",
                "sourceEventId": "original-event-123"
            }
        )
    
    @pytest.mark.asyncio
    async def test_error_handling(self, handler, sample_event):
        """Test error event handling."""
        # Act
        result = await handler.handle(sample_event)
        
        # Assert
        assert result is None  # Error handler returns None
    
    @pytest.mark.asyncio
    async def test_error_with_missing_fields(self, handler):
        """Test error handling with missing fields."""
        # Arrange
        event = create_mock_cloud_event(
            event_type="error",
            data={}  # Missing required fields
        )
        
        # Act
        result = await handler.handle(event)
        
        # Assert
        assert result is None  # Should handle gracefully


class TestHandlerIntegration:
    """Integration tests for handlers."""
    
    @pytest.mark.asyncio
    async def test_handler_chain_processing(self):
        """Test processing through multiple handlers."""
        # Arrange
        services = MockServices()
        
        # Add processors and criteria
        async def processor1(entity, **kwargs):
            entity.add_metadata("step1", True)
            return entity
        
        async def processor2(entity, **kwargs):
            entity.add_metadata("step2", True)
            return entity
        
        async def criteria1(entity, **kwargs):
            return entity.get_metadata("step1") is True
        
        services.processor_manager.add_processor("processor1", processor1)
        services.processor_manager.add_processor("processor2", processor2)
        services.processor_manager.add_criteria("criteria1", criteria1)
        
        # Create handlers
        calc_handler = CalcRequestHandler()
        criteria_handler = CriteriaCalcRequestHandler()
        
        # Create events
        calc_event1 = create_mock_cloud_event(
            event_type=CALC_REQ_EVENT_TYPE,
            data=TestDataBuilder.cloud_event_data(processor_name="processor1")
        )
        
        calc_event2 = create_mock_cloud_event(
            event_type=CALC_REQ_EVENT_TYPE,
            data=TestDataBuilder.cloud_event_data(processor_name="processor2")
        )
        
        criteria_data = TestDataBuilder.cloud_event_data()
        criteria_data["criteriaName"] = "criteria1"
        del criteria_data["processorName"]
        
        criteria_event = create_mock_cloud_event(
            event_type=CRITERIA_CALC_REQ_EVENT_TYPE,
            data=criteria_data
        )
        
        # Act
        result1 = await calc_handler.handle(calc_event1, services)
        result2 = await calc_handler.handle(calc_event2, services)
        result3 = await criteria_handler.handle(criteria_event, services)
        
        # Assert
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        
        # Check processing calls
        assert services.processor_manager.process_calls == 2
        assert services.processor_manager.criteria_calls == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
