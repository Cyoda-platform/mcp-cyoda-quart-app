"""
Integration tests for the complete processor system.
"""
import pytest
from entity.cyoda_entity import CyodaEntity
from entity.job import JobEntity
from common.processor.manager import ProcessorManager, get_processor_manager


class TestProcessorIntegration:
    """Integration tests for the processor system."""
    
    def test_processor_manager_discovers_real_processors(self):
        """Test that the processor manager can discover real processors."""
        # Reset global manager to ensure fresh discovery
        import common.processor.manager
        common.processor.manager._processor_manager = None
        
        # Create manager with actual modules
        manager = get_processor_manager(['workflow.processors', 'workflow.criteria'])
        
        # Should have discovered some processors and criteria
        processors = manager.list_processors()
        criteria = manager.list_criteria()
        
        print(f"Discovered processors: {processors}")
        print(f"Discovered criteria: {criteria}")
        
        # We expect at least some processors and criteria to be discovered
        # Note: Some processors might fail to load due to configuration dependencies
        expected_criteria = ['is_succeeded', 'entity_state']

        # Should have discovered at least one processor
        assert len(processors) > 0, "No processors were discovered"

        # Should have discovered the criteria (they don't have config dependencies)
        for criteria_name in expected_criteria:
            assert criteria_name in criteria, f"Criteria '{criteria_name}' not discovered"

        # If ingest_data processor was discovered, it should be working
        if 'ingest_data' in processors:
            info = manager.get_processor_info('ingest_data')
            assert info is not None
            assert info['name'] == 'ingest_data'
    
    def test_processor_info_retrieval(self):
        """Test retrieving processor information."""
        manager = get_processor_manager(['workflow.processors', 'workflow.criteria'])
        
        # Test processor info
        processors = manager.list_processors()
        if processors:
            processor_name = processors[0]
            info = manager.get_processor_info(processor_name)
            
            assert info is not None
            assert 'name' in info
            assert 'description' in info
            assert 'class' in info
            assert 'module' in info
            assert info['name'] == processor_name
    
    def test_criteria_info_retrieval(self):
        """Test retrieving criteria information."""
        manager = get_processor_manager(['workflow.processors', 'workflow.criteria'])
        
        # Test criteria info
        criteria = manager.list_criteria()
        if criteria:
            criteria_name = criteria[0]
            info = manager.get_criteria_info(criteria_name)
            
            assert info is not None
            assert 'name' in info
            assert 'description' in info
            assert 'class' in info
            assert 'module' in info
            assert info['name'] == criteria_name
    
    @pytest.mark.asyncio
    async def test_criteria_checking_integration(self):
        """Test actual criteria checking with discovered criteria."""
        manager = get_processor_manager(['workflow.processors', 'workflow.criteria'])
        
        criteria_list = manager.list_criteria()
        
        if 'is_succeeded' in criteria_list:
            # Test with a succeeded job
            job = JobEntity(entity_id="test-job-1", state="SUCCEEDED")
            result = await manager.check_criteria('is_succeeded', job)
            assert result is True
            
            # Test with a failed job
            job2 = JobEntity(entity_id="test-job-2", state="FAILED")
            result2 = await manager.check_criteria('is_succeeded', job2)
            assert result2 is False
        
        if 'entity_state' in criteria_list:
            # Test entity state criteria
            entity = CyodaEntity(entity_id="test-entity-1", state="ACTIVE")
            result = await manager.check_criteria('entity_state', entity, expected_states=["ACTIVE"])
            assert result is True
            
            result2 = await manager.check_criteria('entity_state', entity, expected_states=["INACTIVE"])
            assert result2 is False
    
    def test_processor_manager_singleton_behavior(self):
        """Test that processor manager maintains singleton behavior."""
        manager1 = get_processor_manager()
        manager2 = get_processor_manager()
        
        assert manager1 is manager2
        
        # Both should have the same processors and criteria
        assert manager1.list_processors() == manager2.list_processors()
        assert manager1.list_criteria() == manager2.list_criteria()
    
    def test_empty_module_list_handling(self):
        """Test handling of empty module list."""
        manager = ProcessorManager([])
        
        assert len(manager.list_processors()) == 0
        assert len(manager.list_criteria()) == 0
        assert manager.get_processor_info('nonexistent') is None
        assert manager.get_criteria_info('nonexistent') is None
    
    def test_nonexistent_module_handling(self):
        """Test handling of non-existent modules."""
        # Should not crash, just log warnings
        manager = ProcessorManager(['nonexistent.module.that.does.not.exist'])
        
        assert len(manager.list_processors()) == 0
        assert len(manager.list_criteria()) == 0
