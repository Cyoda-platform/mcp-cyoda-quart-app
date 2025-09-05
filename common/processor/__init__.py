"""
Processor system for dynamic entity processing and criteria checking.

This module provides the foundation for the processor system including:
- Base classes for processors and criteria checkers
- Processor manager for automatic discovery and execution
- Error handling for processing operations
"""

from .base import CyodaProcessor, CyodaCriteriaChecker
from .errors import ProcessorError, CriteriaError
from .manager import ProcessorManager, get_processor_manager

__all__ = [
    'CyodaProcessor',
    'CyodaCriteriaChecker', 
    'ProcessorError',
    'CriteriaError',
    'ProcessorManager',
    'get_processor_manager'
]
