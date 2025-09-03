"""
Job entity for representing job/task entities.
"""
from typing import Any, Dict, Optional
from .cyoda_entity import CyodaEntity


class JobEntity(CyodaEntity):
    """
    Entity representing a job or task.
    
    This is a specialized entity type for jobs that can be processed
    by the processor system.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a job entity.
        
        Args:
            **kwargs: Entity data including entity_id, state, metadata, etc.
        """
        # Set default entity_type for jobs
        if 'entity_type' not in kwargs:
            kwargs['entity_type'] = 'job'
        
        super().__init__(**kwargs)
    
    def is_completed(self) -> bool:
        """
        Check if the job is completed (succeeded or failed).
        
        Returns:
            True if the job is in a completed state, False otherwise.
        """
        return self.state in ['SUCCEEDED', 'FAILED', 'COMPLETED']
    
    def is_succeeded(self) -> bool:
        """
        Check if the job has succeeded.
        
        Returns:
            True if the job succeeded, False otherwise.
        """
        return self.state == 'SUCCEEDED'
    
    def is_failed(self) -> bool:
        """
        Check if the job has failed.
        
        Returns:
            True if the job failed, False otherwise.
        """
        return self.state == 'FAILED'
    
    def is_running(self) -> bool:
        """
        Check if the job is currently running.
        
        Returns:
            True if the job is running, False otherwise.
        """
        return self.state in ['RUNNING', 'PROCESSING', 'IN_PROGRESS']
    
    def get_progress(self) -> Optional[float]:
        """
        Get the job progress as a percentage.
        
        Returns:
            Progress percentage (0.0 to 100.0) or None if not available.
        """
        progress = self.get_metadata('progress')
        if progress is not None:
            try:
                return float(progress)
            except (ValueError, TypeError):
                return None
        return None
    
    def set_progress(self, progress: float) -> None:
        """
        Set the job progress.
        
        Args:
            progress: Progress percentage (0.0 to 100.0).
        """
        self.add_metadata('progress', progress)
    
    def get_error_message(self) -> Optional[str]:
        """
        Get the error message if the job failed.
        
        Returns:
            Error message or None if no error.
        """
        return self.get_metadata('error_message')
    
    def set_error_message(self, error_message: str) -> None:
        """
        Set the error message for a failed job.
        
        Args:
            error_message: The error message to set.
        """
        self.add_metadata('error_message', error_message)
    
    def get_result(self) -> Optional[Any]:
        """
        Get the job result if available.
        
        Returns:
            Job result or None if not available.
        """
        return self.get_metadata('result')
    
    def set_result(self, result: Any) -> None:
        """
        Set the job result.
        
        Args:
            result: The job result to set.
        """
        self.add_metadata('result', result)
