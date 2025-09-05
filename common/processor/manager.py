"""
Processor manager for automatic discovery and execution of processors and criteria checkers.
"""
import importlib
import inspect
import logging
import pkgutil
from typing import Any, Dict, List, Optional, Type

from entity.cyoda_entity import CyodaEntity
from common.interfaces.services import IProcessorManager

from .base import CyodaProcessor, CyodaCriteriaChecker
from .errors import ProcessorError, CriteriaError, ProcessorNotFoundError, CriteriaNotFoundError

logger = logging.getLogger(__name__)


class ProcessorManager(IProcessorManager):
    """
    Manager for processors and criteria checkers with automatic discovery.
    
    This manager automatically discovers and registers processors and criteria checkers
    from specified modules using OOP-friendly discovery methods.
    """
    
    def __init__(self, modules: Optional[List[str]] = None):
        """
        Initialize the processor manager.
        
        Args:
            modules: List of module names to scan for processors and criteria
        """
        self.processors: Dict[str, CyodaProcessor] = {}
        self.criteria: Dict[str, CyodaCriteriaChecker] = {}
        self.modules = modules or []
        
        # Automatically discover and register processors and criteria
        self._discover_and_register()
    
    def _discover_and_register(self):
        """Discover and register all processors and criteria from specified modules."""
        for module_name in self.modules:
            try:
                self._discover_from_module(module_name)
            except Exception as e:
                logger.warning(f"Failed to discover from module '{module_name}': {e}")
    
    def _discover_from_module(self, module_name: str):
        """
        Discover processors and criteria from a specific module.
        
        Args:
            module_name: Name of the module to scan
        """
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Check if it's a package and scan submodules
            if hasattr(module, '__path__'):
                self._discover_from_package(module)
            else:
                self._discover_from_single_module(module)
                
        except ImportError as e:
            logger.warning(f"Could not import module '{module_name}': {e}")
    
    def _discover_from_package(self, package):
        """
        Discover processors and criteria from a package by scanning all submodules.
        
        Args:
            package: The package to scan
        """
        package_name = package.__name__
        
        # Walk through all modules in the package
        for importer, modname, ispkg in pkgutil.walk_packages(
            package.__path__, 
            package_name + "."
        ):
            try:
                module = importlib.import_module(modname)
                self._discover_from_single_module(module)
            except Exception as e:
                logger.warning(f"Failed to import submodule '{modname}': {e}")
    
    def _discover_from_single_module(self, module):
        """
        Discover processors and criteria from a single module.
        
        Args:
            module: The module to scan
        """
        # Get all classes from the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip if the class is not defined in this module
            if obj.__module__ != module.__name__:
                continue
            
            # Check if it's a processor
            if (issubclass(obj, CyodaProcessor) and 
                obj is not CyodaProcessor and 
                not inspect.isabstract(obj)):
                self._register_processor_class(obj)
            
            # Check if it's a criteria checker
            elif (issubclass(obj, CyodaCriteriaChecker) and 
                  obj is not CyodaCriteriaChecker and 
                  not inspect.isabstract(obj)):
                self._register_criteria_class(obj)
    
    def _register_processor_class(self, processor_class: Type[CyodaProcessor]):
        """
        Register a processor class by instantiating it.
        
        Args:
            processor_class: The processor class to register
        """
        try:
            # Try to instantiate with default parameters
            processor = processor_class()
            self.register_processor(processor)
            logger.info(f"Registered processor: {processor.name} ({processor_class.__name__})")
        except Exception as e:
            logger.error(f"Failed to instantiate processor {processor_class.__name__}: {e}")
    
    def _register_criteria_class(self, criteria_class: Type[CyodaCriteriaChecker]):
        """
        Register a criteria checker class by instantiating it.
        
        Args:
            criteria_class: The criteria checker class to register
        """
        try:
            # Try to instantiate with default parameters
            criteria = criteria_class()
            self.register_criteria(criteria)
            logger.info(f"Registered criteria: {criteria.name} ({criteria_class.__name__})")
        except Exception as e:
            logger.error(f"Failed to instantiate criteria {criteria_class.__name__}: {e}")
    
    def register_processor(self, processor: CyodaProcessor):
        """
        Manually register a processor instance.
        
        Args:
            processor: The processor instance to register
        """
        self.processors[processor.name] = processor
        logger.debug(f"Registered processor: {processor.name}")
    
    def register_criteria(self, criteria: CyodaCriteriaChecker):
        """
        Manually register a criteria checker instance.
        
        Args:
            criteria: The criteria checker instance to register
        """
        self.criteria[criteria.name] = criteria
        logger.debug(f"Registered criteria: {criteria.name}")
    
    async def process_entity(self, processor_name: str, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """
        Process an entity using the specified processor.
        
        Args:
            processor_name: Name of the processor to use
            entity: The entity to process
            **kwargs: Additional processing parameters
            
        Returns:
            The processed entity
            
        Raises:
            ProcessorNotFoundError: If the processor is not found
            ProcessorError: If processing fails
        """
        if processor_name not in self.processors:
            raise ProcessorNotFoundError(processor_name)
        
        processor = self.processors[processor_name]
        
        # Check if the processor can handle this entity
        if not processor.can_process(entity, **kwargs):
            raise ProcessorError(
                processor_name=processor_name,
                message=f"Processor cannot handle entity of type {entity.entity_type}",
                entity_id=entity.entity_id
            )
        
        try:
            return await processor.process(entity, **kwargs)
        except Exception as e:
            if isinstance(e, ProcessorError):
                raise
            raise ProcessorError(
                processor_name=processor_name,
                message=str(e),
                original_error=e,
                entity_id=entity.entity_id
            )
    
    async def check_criteria(self, criteria_name: str, entity: CyodaEntity, **kwargs) -> bool:
        """
        Check if entity meets the specified criteria.
        
        Args:
            criteria_name: Name of the criteria checker to use
            entity: The entity to check
            **kwargs: Additional criteria parameters
            
        Returns:
            True if the entity meets the criteria, False otherwise
            
        Raises:
            CriteriaNotFoundError: If the criteria checker is not found
            CriteriaError: If criteria checking fails
        """
        if criteria_name not in self.criteria:
            raise CriteriaNotFoundError(criteria_name)
        
        criteria = self.criteria[criteria_name]
        
        # Check if the criteria checker can handle this entity
        if not criteria.can_check(entity, **kwargs):
            raise CriteriaError(
                criteria_name=criteria_name,
                message=f"Criteria checker cannot handle entity of type {entity.entity_type}",
                entity_id=entity.entity_id
            )
        
        try:
            return await criteria.check(entity, **kwargs)
        except Exception as e:
            if isinstance(e, CriteriaError):
                raise
            raise CriteriaError(
                criteria_name=criteria_name,
                message=str(e),
                original_error=e,
                entity_id=entity.entity_id
            )
    
    def list_processors(self) -> List[str]:
        """List available processors."""
        return list(self.processors.keys())
    
    def list_criteria(self) -> List[str]:
        """List available criteria."""
        return list(self.criteria.keys())
    
    def get_processor_info(self, processor_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a processor."""
        if processor_name in self.processors:
            return self.processors[processor_name].get_info()
        return None
    
    def get_criteria_info(self, criteria_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a criteria checker."""
        if criteria_name in self.criteria:
            return self.criteria[criteria_name].get_info()
        return None


# Global processor manager instance
_processor_manager: Optional[ProcessorManager] = None


def get_processor_manager(modules: Optional[List[str]] = None) -> ProcessorManager:
    """
    Get the global processor manager instance.
    
    Args:
        modules: List of module names to scan for processors and criteria.
                If None and no global instance exists, uses default modules.
    
    Returns:
        The global processor manager instance
    """
    global _processor_manager
    
    if _processor_manager is None:
        # Use provided modules or default ones
        if modules is None:
            modules = ['workflow.processors', 'workflow.criteria']
        _processor_manager = ProcessorManager(modules)
    
    return _processor_manager
