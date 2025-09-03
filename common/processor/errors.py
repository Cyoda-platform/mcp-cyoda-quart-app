"""
Error classes for the processor system.
"""
from typing import Any, Dict, Optional


class ProcessorError(Exception):
    """Base exception for processor-related errors."""
    
    def __init__(
        self,
        processor_name: str,
        message: str,
        original_error: Optional[Exception] = None,
        entity_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the processor error.
        
        Args:
            processor_name: Name of the processor that failed
            message: Error message
            original_error: The original exception that caused this error
            entity_id: ID of the entity being processed when error occurred
            context: Additional context information
        """
        self.processor_name = processor_name
        self.message = message
        self.original_error = original_error
        self.entity_id = entity_id
        self.context = context or {}
        
        # Build the full error message
        full_message = f"Processor '{processor_name}' failed: {message}"
        if entity_id:
            full_message += f" (entity_id: {entity_id})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            'error_type': 'ProcessorError',
            'processor_name': self.processor_name,
            'message': self.message,
            'entity_id': self.entity_id,
            'context': self.context,
            'original_error': str(self.original_error) if self.original_error else None
        }


class CriteriaError(Exception):
    """Base exception for criteria checker-related errors."""
    
    def __init__(
        self,
        criteria_name: str,
        message: str,
        original_error: Optional[Exception] = None,
        entity_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the criteria error.
        
        Args:
            criteria_name: Name of the criteria checker that failed
            message: Error message
            original_error: The original exception that caused this error
            entity_id: ID of the entity being checked when error occurred
            context: Additional context information
        """
        self.criteria_name = criteria_name
        self.message = message
        self.original_error = original_error
        self.entity_id = entity_id
        self.context = context or {}
        
        # Build the full error message
        full_message = f"Criteria '{criteria_name}' failed: {message}"
        if entity_id:
            full_message += f" (entity_id: {entity_id})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            'error_type': 'CriteriaError',
            'criteria_name': self.criteria_name,
            'message': self.message,
            'entity_id': self.entity_id,
            'context': self.context,
            'original_error': str(self.original_error) if self.original_error else None
        }


class ProcessorNotFoundError(ProcessorError):
    """Exception raised when a requested processor is not found."""
    
    def __init__(self, processor_name: str):
        super().__init__(
            processor_name=processor_name,
            message=f"Processor '{processor_name}' not found"
        )


class CriteriaNotFoundError(CriteriaError):
    """Exception raised when a requested criteria checker is not found."""
    
    def __init__(self, criteria_name: str):
        super().__init__(
            criteria_name=criteria_name,
            message=f"Criteria checker '{criteria_name}' not found"
        )
