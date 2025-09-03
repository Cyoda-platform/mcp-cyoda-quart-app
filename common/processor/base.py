"""
Base classes for processors and criteria checkers.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CyodaProcessor(ABC):
    """Base class for all entity processors."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the processor.
        
        Args:
            name: Unique name for the processor
            description: Human-readable description of what the processor does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """
        Process the entity.
        
        Args:
            entity: The entity to process
            **kwargs: Additional processing parameters
            
        Returns:
            The processed entity
            
        Raises:
            ProcessorError: If processing fails
        """
        pass
    
    @abstractmethod
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """
        Check if this processor can handle the given entity.
        
        Args:
            entity: The entity to check
            **kwargs: Additional parameters
            
        Returns:
            True if this processor can handle the entity, False otherwise
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            Dictionary containing processor information
        """
        return {
            'name': self.name,
            'description': self.description,
            'class': self.__class__.__name__,
            'module': self.__class__.__module__
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"


class CyodaCriteriaChecker(ABC):
    """Base class for all criteria checkers."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the criteria checker.
        
        Args:
            name: Unique name for the criteria checker
            description: Human-readable description of what the criteria checks
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """
        Check if the entity meets the criteria.
        
        Args:
            entity: The entity to check
            **kwargs: Additional criteria parameters
            
        Returns:
            True if the entity meets the criteria, False otherwise
            
        Raises:
            CriteriaError: If criteria checking fails
        """
        pass
    
    @abstractmethod
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """
        Check if this criteria checker can evaluate the given entity.
        
        Args:
            entity: The entity to check
            **kwargs: Additional parameters
            
        Returns:
            True if this criteria checker can evaluate the entity, False otherwise
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this criteria checker.
        
        Returns:
            Dictionary containing criteria checker information
        """
        return {
            'name': self.name,
            'description': self.description,
            'class': self.__class__.__name__,
            'module': self.__class__.__module__
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"
