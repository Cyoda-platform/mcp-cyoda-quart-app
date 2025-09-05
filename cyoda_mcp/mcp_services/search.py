"""
Search Service for MCP

This service provides comprehensive search functionality for the MCP server,
using the existing entity service with find_all and search methods.
"""

import logging
from typing import Dict, Any, List, Optional
from common.service.entity_service import EntityService, SearchConditionRequest
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)


class SearchService:
    """Service class for search operations using entity service find_all and search methods."""
    
    def __init__(self, entity_service: EntityService):
        """
        Initialize the search service.
        
        Args:
            entity_service: The injected entity service
        """
        self.entity_service = entity_service
        logger.info("SearchService initialized")
    
    async def find_all_entities(self, entity_class: str, entity_version: str = ENTITY_VERSION) -> Dict[str, Any]:
        """
        Find all entities of a specific type using entity_service.find_all().
        
        Args:
            entity_class: The type of entity to retrieve
            entity_version: The entity model version
            
        Returns:
            Dictionary containing all entities or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_class": entity_class
                }
            
            results = await self.entity_service.find_all(entity_class, entity_version)
            
            entities = [
                {
                    "id": r.get_id(),
                    "data": r.data,
                    "state": r.metadata.state,
                    "created_at": r.metadata.created_at,
                    "updated_at": r.metadata.updated_at
                }
                for r in results
            ]
            
            logger.info(f"Found {len(entities)} entities of type {entity_class}")
            
            return {
                "success": True,
                "count": len(entities),
                "entities": entities,
                "entity_class": entity_class,
                "entity_version": entity_version
            }
            
        except Exception as e:
            logger.exception(f"Failed to find all entities of type {entity_class}: {e}")
            return {
                "success": False,
                "error": str(e),
                "entity_class": entity_class
            }
    
    async def search_entities(
        self, 
        entity_class: str, 
        search_conditions: Dict[str, Any], 
        entity_version: str = ENTITY_VERSION,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        operator: str = "and"
    ) -> Dict[str, Any]:
        """
        Search entities with specific conditions using entity_service.search().
        
        Args:
            entity_class: The type of entity to search
            search_conditions: Dictionary of search conditions (field: value pairs)
            entity_version: The entity model version
            limit: Maximum number of results to return
            offset: Number of results to skip
            operator: Logical operator for multiple conditions ("and" or "or")
            
        Returns:
            Dictionary containing search results or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_class": entity_class
                }
            
            # Build search request from conditions
            builder = SearchConditionRequest.builder()
            
            for field, value in search_conditions.items():
                if isinstance(value, dict) and "operator" in value:
                    # Advanced condition format: {"operator": "contains", "value": "text"}
                    op = value.get("operator", "eq")
                    val = value.get("value")
                    builder.add_condition(field, op, val)
                else:
                    # Simple condition format: field: value (defaults to equals)
                    builder.equals(field, value)
            
            # Set additional parameters
            builder.operator(operator)
            if limit:
                builder.limit(limit)
            if offset:
                builder.offset(offset)
            
            search_request = builder.build()
            results = await self.entity_service.search(entity_class, search_request, entity_version)
            
            entities = [
                {
                    "id": r.get_id(),
                    "data": r.data,
                    "state": r.metadata.state,
                    "created_at": r.metadata.created_at,
                    "updated_at": r.metadata.updated_at
                }
                for r in results
            ]
            
            logger.info(f"Search found {len(entities)} entities of type {entity_class}")
            
            return {
                "success": True,
                "count": len(entities),
                "entities": entities,
                "search_conditions": search_conditions,
                "entity_class": entity_class,
                "entity_version": entity_version,
                "limit": limit,
                "offset": offset,
                "operator": operator
            }
            
        except Exception as e:
            logger.exception(f"Failed to search entities of type {entity_class}: {e}")
            return {
                "success": False,
                "error": str(e),
                "entity_class": entity_class,
                "search_conditions": search_conditions
            }
    
    async def search_entities_advanced(
        self,
        entity_class: str,
        conditions: List[Dict[str, Any]],
        entity_version: str = ENTITY_VERSION,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        operator: str = "and"
    ) -> Dict[str, Any]:
        """
        Advanced search with multiple complex conditions.
        
        Args:
            entity_class: The type of entity to search
            conditions: List of condition dictionaries with field, operator, and value
            entity_version: The entity model version
            limit: Maximum number of results to return
            offset: Number of results to skip
            operator: Logical operator for multiple conditions ("and" or "or")
            
        Returns:
            Dictionary containing search results or error information
        """
        try:
            if not self.entity_service:
                return {
                    "success": False,
                    "error": "Entity service not available",
                    "entity_class": entity_class
                }
            
            # Build search request from advanced conditions
            builder = SearchConditionRequest.builder()
            
            for condition in conditions:
                field = condition.get("field")
                op = condition.get("operator", "eq")
                value = condition.get("value")
                
                if not field or value is None:
                    continue
                    
                builder.add_condition(field, op, value)
            
            # Set additional parameters
            builder.operator(operator)
            if limit:
                builder.limit(limit)
            if offset:
                builder.offset(offset)
            
            search_request = builder.build()
            results = await self.entity_service.search(entity_class, search_request, entity_version)
            
            entities = [
                {
                    "id": r.get_id(),
                    "data": r.data,
                    "state": r.metadata.state,
                    "created_at": r.metadata.created_at,
                    "updated_at": r.metadata.updated_at
                }
                for r in results
            ]
            
            logger.info(f"Advanced search found {len(entities)} entities of type {entity_class}")
            
            return {
                "success": True,
                "count": len(entities),
                "entities": entities,
                "conditions": conditions,
                "entity_class": entity_class,
                "entity_version": entity_version,
                "limit": limit,
                "offset": offset,
                "operator": operator
            }
            
        except Exception as e:
            logger.exception(f"Failed to perform advanced search on {entity_class}: {e}")
            return {
                "success": False,
                "error": str(e),
                "entity_class": entity_class,
                "conditions": conditions
            }
