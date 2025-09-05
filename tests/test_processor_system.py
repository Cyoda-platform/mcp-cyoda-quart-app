"""
Test the processor system functionality.
"""
import pytest
from unittest.mock import Mock, AsyncMock

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaProcessor, CyodaCriteriaChecker
from common.processor.errors import ProcessorError, CriteriaError, ProcessorNotFoundError, CriteriaNotFoundError
from common.processor.manager import ProcessorManager


class TestProcessor(CyodaProcessor):
    """Test processor for unit tests."""
    
    def __init__(self, name: str = "test_processor", description: str = "Test processor"):
        super().__init__(name, description)
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process the entity by adding test metadata."""
        entity.add_metadata("processed_by", self.name)
        entity.add_metadata("test_param", kwargs.get("test_param", "default"))
        return entity
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Can process any entity."""
        return True


class TestCriteria(CyodaCriteriaChecker):
    """Test criteria checker for unit tests."""
    
    def __init__(self, name: str = "test_criteria", description: str = "Test criteria"):
        super().__init__(name, description)
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if entity has test metadata."""
        return entity.get_metadata("test_flag") == "true"
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Can check any entity."""
        return True


class TestProcessorSystem:
    """Test the processor system."""
    
    def test_processor_manager_initialization(self):
        """Test processor manager can be initialized."""
        manager = ProcessorManager([])
        assert manager is not None
        assert len(manager.processors) == 0
        assert len(manager.criteria) == 0
    
    def test_manual_processor_registration(self):
        """Test manual registration of processors."""
        manager = ProcessorManager([])
        processor = TestProcessor()
        
        manager.register_processor(processor)
        
        assert "test_processor" in manager.processors
        assert manager.processors["test_processor"] == processor
        assert "test_processor" in manager.list_processors()
    
    def test_manual_criteria_registration(self):
        """Test manual registration of criteria."""
        manager = ProcessorManager([])
        criteria = TestCriteria()
        
        manager.register_criteria(criteria)
        
        assert "test_criteria" in manager.criteria
        assert manager.criteria["test_criteria"] == criteria
        assert "test_criteria" in manager.list_criteria()
    
    @pytest.mark.asyncio
    async def test_process_entity_success(self):
        """Test successful entity processing."""
        manager = ProcessorManager([])
        processor = TestProcessor()
        manager.register_processor(processor)
        
        entity = CyodaEntity(entity_id="test-123", entity_type="test")
        
        result = await manager.process_entity("test_processor", entity, test_param="custom_value")
        
        assert result.get_metadata("processed_by") == "test_processor"
        assert result.get_metadata("test_param") == "custom_value"
    
    @pytest.mark.asyncio
    async def test_process_entity_not_found(self):
        """Test processing with non-existent processor."""
        manager = ProcessorManager([])
        entity = CyodaEntity(entity_id="test-123", entity_type="test")
        
        with pytest.raises(ProcessorNotFoundError) as exc_info:
            await manager.process_entity("non_existent", entity)
        
        assert "non_existent" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_check_criteria_success(self):
        """Test successful criteria checking."""
        manager = ProcessorManager([])
        criteria = TestCriteria()
        manager.register_criteria(criteria)
        
        # Entity that meets criteria
        entity = CyodaEntity(entity_id="test-123", entity_type="test")
        entity.add_metadata("test_flag", "true")
        
        result = await manager.check_criteria("test_criteria", entity)
        assert result is True
        
        # Entity that doesn't meet criteria
        entity2 = CyodaEntity(entity_id="test-456", entity_type="test")
        entity2.add_metadata("test_flag", "false")
        
        result2 = await manager.check_criteria("test_criteria", entity2)
        assert result2 is False
    
    @pytest.mark.asyncio
    async def test_check_criteria_not_found(self):
        """Test criteria checking with non-existent criteria."""
        manager = ProcessorManager([])
        entity = CyodaEntity(entity_id="test-123", entity_type="test")
        
        with pytest.raises(CriteriaNotFoundError) as exc_info:
            await manager.check_criteria("non_existent", entity)
        
        assert "non_existent" in str(exc_info.value)
    
    def test_get_processor_info(self):
        """Test getting processor information."""
        manager = ProcessorManager([])
        processor = TestProcessor()
        manager.register_processor(processor)
        
        info = manager.get_processor_info("test_processor")
        
        assert info is not None
        assert info["name"] == "test_processor"
        assert info["description"] == "Test processor"
        assert "class" in info
        assert "module" in info
    
    def test_get_criteria_info(self):
        """Test getting criteria information."""
        manager = ProcessorManager([])
        criteria = TestCriteria()
        manager.register_criteria(criteria)
        
        info = manager.get_criteria_info("test_criteria")
        
        assert info is not None
        assert info["name"] == "test_criteria"
        assert info["description"] == "Test criteria"
        assert "class" in info
        assert "module" in info
    
    def test_processor_base_class_methods(self):
        """Test base processor class methods."""
        processor = TestProcessor("custom_name", "Custom description")
        
        assert processor.name == "custom_name"
        assert processor.description == "Custom description"
        
        info = processor.get_info()
        assert info["name"] == "custom_name"
        assert info["description"] == "Custom description"
        
        assert "custom_name" in str(processor)
        assert "custom_name" in repr(processor)
    
    def test_criteria_base_class_methods(self):
        """Test base criteria class methods."""
        criteria = TestCriteria("custom_criteria", "Custom criteria description")
        
        assert criteria.name == "custom_criteria"
        assert criteria.description == "Custom criteria description"
        
        info = criteria.get_info()
        assert info["name"] == "custom_criteria"
        assert info["description"] == "Custom criteria description"
        
        assert "custom_criteria" in str(criteria)
        assert "custom_criteria" in repr(criteria)
    
    def test_processor_error_creation(self):
        """Test processor error creation and methods."""
        error = ProcessorError(
            processor_name="test_processor",
            message="Test error",
            entity_id="test-123",
            context={"key": "value"}
        )
        
        assert error.processor_name == "test_processor"
        assert error.message == "Test error"
        assert error.entity_id == "test-123"
        assert error.context == {"key": "value"}
        
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "ProcessorError"
        assert error_dict["processor_name"] == "test_processor"
        assert error_dict["message"] == "Test error"
        assert error_dict["entity_id"] == "test-123"
        assert error_dict["context"] == {"key": "value"}
    
    def test_criteria_error_creation(self):
        """Test criteria error creation and methods."""
        error = CriteriaError(
            criteria_name="test_criteria",
            message="Test criteria error",
            entity_id="test-456",
            context={"criteria_key": "criteria_value"}
        )
        
        assert error.criteria_name == "test_criteria"
        assert error.message == "Test criteria error"
        assert error.entity_id == "test-456"
        assert error.context == {"criteria_key": "criteria_value"}
        
        error_dict = error.to_dict()
        assert error_dict["error_type"] == "CriteriaError"
        assert error_dict["criteria_name"] == "test_criteria"
        assert error_dict["message"] == "Test criteria error"
        assert error_dict["entity_id"] == "test-456"
        assert error_dict["context"] == {"criteria_key": "criteria_value"}
