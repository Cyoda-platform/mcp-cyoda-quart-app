"""
Enhanced Entity Service Implementation

This module provides a comprehensive implementation of the EntityService interface
with proper error handling, type safety, and performance optimizations.
"""

import logging
import threading
from typing import Any, List, Optional, Dict
from datetime import datetime

from common.config.config import CHAT_REPOSITORY
from common.repository.crud_repository import CrudRepository
from common.service.entity_service import (
    EntityService,
    EntityResponse,
    EntityMetadata,
    SearchConditionRequest,
    SearchCondition
)
from common.utils.utils import parse_entity

logger = logging.getLogger('quart')


class EntityServiceError(Exception):
    """Custom exception for entity service operations."""

    def __init__(self, message: str, entity_class: str = None, entity_id: str = None):
        super().__init__(message)
        self.entity_class = entity_class
        self.entity_id = entity_id

class EntityServiceImpl(EntityService):
    """
    Enhanced implementation of EntityService with comprehensive functionality.

    Features:
    - Thread-safe singleton pattern
    - Comprehensive error handling
    - Type-safe operations
    - Performance optimizations
    - Full interface compliance
    """

    _instance: Optional['EntityServiceImpl'] = None
    _lock = threading.Lock()

    def __init__(self, repository: CrudRepository, model_registry: Dict[str, Any] = None):
        """
        Initialize EntityService implementation.

        Args:
            repository: CRUD repository for data operations
            model_registry: Registry of entity model classes
        """
        self._repository = repository
        self._model_registry = model_registry or {}
        logger.info("EntityServiceImpl initialized")

    @classmethod
    def get_instance(cls, repository: CrudRepository = None, model_registry: Dict[str, Any] = None) -> 'EntityServiceImpl':
        """
        Get singleton instance of EntityServiceImpl.

        Args:
            repository: CRUD repository for data operations (required for first initialization)
            model_registry: Registry of entity model classes

        Returns:
            EntityServiceImpl instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if repository is None:
                        raise ValueError("Repository is required for first initialization")
                    # Create instance directly to avoid infinite recursion
                    cls._instance = super(EntityServiceImpl, cls).__new__(cls)
                    cls._instance.__init__(repository, model_registry)
                    logger.info("EntityServiceImpl singleton created")
        elif repository is not None:
            # If instance exists but repository is provided, log a warning
            logger.warning("EntityServiceImpl instance already exists. Ignoring provided repository.")

        return cls._instance

    def __new__(cls, repository: CrudRepository = None, model_registry: Dict[str, Any] = None):
        """Maintain backward compatibility with old constructor."""
        if repository is not None:
            return cls.get_instance(repository, model_registry)
        elif cls._instance is not None:
            return cls._instance
        else:
            # If no repository and no instance, raise error
            raise ValueError("Repository is required for EntityServiceImpl initialization. Use get_instance() or provide repository.")

    # ========================================
    # HELPER METHODS
    # ========================================

    def _create_entity_response(self, data: Any, entity_id: str = None, state: str = None) -> EntityResponse:
        """
        Create EntityResponse with proper metadata.

        Args:
            data: Entity data
            entity_id: Technical UUID
            state: Entity state

        Returns:
            EntityResponse with data and metadata
        """
        # Extract technical_id from data if not provided
        if entity_id is None and isinstance(data, dict):
            entity_id = data.get('technical_id') or data.get('id')

        # Extract state from data if not provided
        if state is None and isinstance(data, dict):
            state = data.get('current_state') or data.get('state')

        metadata = EntityMetadata(
            id=entity_id or "unknown",
            state=state,
            created_at=datetime.now(),
            entity_type="entity"
        )

        return EntityResponse(data=data, metadata=metadata)

    def _parse_entity_data(self, data: Any, entity_class: str) -> Any:
        """
        Parse entity data using model registry.

        Args:
            data: Raw entity data
            entity_class: Entity class name

        Returns:
            Parsed entity data
        """
        if not data:
            return data

        model_cls = self._model_registry.get(entity_class.lower())
        if model_cls:
            return parse_entity(model_cls, data)
        return data

    def _handle_repository_error(self, data: Any, operation: str, entity_class: str = None, entity_id: str = None) -> Any:
        """
        Handle repository response errors.

        Args:
            data: Repository response data
            operation: Operation name for logging
            entity_class: Entity class name
            entity_id: Entity ID

        Returns:
            Processed data or raises exception

        Raises:
            EntityServiceError: If repository returned an error
        """
        if isinstance(data, dict) and data.get("errorMessage"):
            error_msg = f"{operation} failed: {data.get('errorMessage')}"
            logger.error(f"{error_msg} - Entity: {entity_class}, ID: {entity_id}")
            raise EntityServiceError(error_msg, entity_class, entity_id)

        return data

    async def _get_repository_meta(self, token: str, entity_class: str, entity_version: str, additional_meta: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get repository metadata with optional additional metadata.

        Args:
            token: Authentication token
            entity_class: Entity class name
            entity_version: Entity version
            additional_meta: Additional metadata to merge

        Returns:
            Complete metadata dictionary
        """
        meta = await self._repository.get_meta(token, entity_class, entity_version)
        if additional_meta:
            meta.update(additional_meta)
        return meta

    # ========================================
    # PRIMARY RETRIEVAL METHODS
    # ========================================

    async def get_by_id(self, entity_id: str, entity_class: str, entity_version: str = "1.0") -> Optional[EntityResponse]:
        """
        Get entity by technical UUID (FASTEST - use when you have the UUID).

        Args:
            entity_id: Technical UUID
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            EntityResponse with entity and metadata, or None if not found
        """
        try:
            # Use empty token for now - this should be injected properly in production
            meta = await self._get_repository_meta("", entity_class, entity_version)

            data = await self._repository.find_by_id(meta, entity_id)
            if not data:
                return None

            # Handle repository errors
            data = self._handle_repository_error(data, "get_by_id", entity_class, entity_id)

            # Parse entity data
            parsed_data = self._parse_entity_data(data, entity_class)

            # Create response
            return self._create_entity_response(parsed_data, entity_id)

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to get entity by ID: {entity_id}")
            raise EntityServiceError(f"Get by ID failed: {str(e)}", entity_class, entity_id)

    async def find_by_business_id(
        self,
        entity_class: str,
        business_id: str,
        business_id_field: str,
        entity_version: str = "1.0"
    ) -> Optional[EntityResponse]:
        """
        Find entity by business identifier (MEDIUM SPEED - use for user-facing IDs).

        Args:
            entity_class: Entity class/model name
            business_id: Business identifier value (e.g., "CART-123")
            business_id_field: Field name containing the business ID (e.g., "cart_id")
            entity_version: Entity model version

        Returns:
            EntityResponse with entity and metadata, or None if not found
        """
        try:
            # Create search condition for business ID
            condition = {business_id_field: business_id}

            # Use search to find by business ID
            search_request = SearchConditionRequest.builder().equals(business_id_field, business_id).limit(1).build()
            results = await self.search(entity_class, search_request, entity_version)

            return results[0] if results else None

        except Exception as e:
            logger.exception(f"Failed to find entity by business ID: {business_id}")
            raise EntityServiceError(f"Find by business ID failed: {str(e)}", entity_class, business_id)

    async def find_all(self, entity_class: str, entity_version: str = "1.0") -> List[EntityResponse]:
        """
        Get all entities of a type (SLOW - use sparingly).

        Args:
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            List of EntityResponse with entities and metadata
        """
        try:
            meta = await self._get_repository_meta("", entity_class, entity_version)

            data = await self._repository.find_all(meta)

            # Handle repository errors
            data = self._handle_repository_error(data, "find_all", entity_class)

            if not data:
                return []

            # Parse and create responses
            results = []
            for item in data if isinstance(data, list) else [data]:
                parsed_item = self._parse_entity_data(item, entity_class)
                response = self._create_entity_response(parsed_item)
                results.append(response)

            logger.debug(f"Found {len(results)} entities of type {entity_class}")
            return results

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to find all entities of type: {entity_class}")
            raise EntityServiceError(f"Find all failed: {str(e)}", entity_class)

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1.0"
    ) -> List[EntityResponse]:
        """
        Search entities with complex conditions (SLOWEST - most flexible).

        Args:
            entity_class: Entity class/model name
            condition: Search condition
            entity_version: Entity model version

        Returns:
            List of EntityResponse with entities and metadata
        """
        try:
            meta = await self._get_repository_meta("", entity_class, entity_version)

            # Convert SearchConditionRequest to repository format
            criteria = self._convert_search_condition(condition)

            data = await self._repository.find_all_by_criteria(meta, criteria)

            # Handle repository errors
            data = self._handle_repository_error(data, "search", entity_class)

            if not data:
                return []

            # Parse and create responses
            results = []
            for item in data if isinstance(data, list) else [data]:
                parsed_item = self._parse_entity_data(item, entity_class)
                response = self._create_entity_response(parsed_item)
                results.append(response)

            # Apply limit if specified
            if condition.limit and len(results) > condition.limit:
                results = results[:condition.limit]

            logger.debug(f"Search found {len(results)} entities of type {entity_class}")
            return results

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to search entities of type: {entity_class}")
            raise EntityServiceError(f"Search failed: {str(e)}", entity_class)

    def _convert_search_condition(self, condition: SearchConditionRequest) -> Dict[str, Any]:
        """
        Convert SearchConditionRequest to repository-compatible format.

        Args:
            condition: Search condition request

        Returns:
            Repository-compatible criteria dictionary
        """
        if len(condition.conditions) == 1:
            # Single condition - simple format
            cond = condition.conditions[0]
            if cond.operator == "eq":
                return {cond.field: cond.value}
            else:
                return {cond.field: {cond.operator: cond.value}}
        else:
            # Multiple conditions - complex format
            criteria = {condition.operator: []}
            for cond in condition.conditions:
                if cond.operator == "eq":
                    criteria[condition.operator].append({cond.field: cond.value})
                else:
                    criteria[condition.operator].append({cond.field: {cond.operator: cond.value}})
            return criteria

    # ========================================
    # PRIMARY MUTATION METHODS
    # ========================================

    async def save(self, entity: Dict[str, Any], entity_class: str, entity_version: str = "1.0") -> EntityResponse:
        """
        Save a new entity (CREATE operation).

        Args:
            entity: New entity data to save
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            EntityResponse with saved entity and metadata
        """
        try:
            meta = await self._get_repository_meta("", entity_class, entity_version)

            entity_id = await self._repository.save(meta, entity)

            if not entity_id:
                raise EntityServiceError("Save operation returned no entity ID", entity_class)

            # Add technical_id to entity data
            entity_with_id = {**entity, "technical_id": entity_id}

            # Parse entity data
            parsed_entity = self._parse_entity_data(entity_with_id, entity_class)

            # Create response
            response = self._create_entity_response(parsed_entity, entity_id, "active")

            logger.debug(f"Saved entity {entity_id} of type {entity_class}")
            return response

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to save entity of type: {entity_class}")
            raise EntityServiceError(f"Save failed: {str(e)}", entity_class)

    async def update(
        self,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str] = None,
        entity_version: str = "1.0"
    ) -> EntityResponse:
        """
        Update existing entity by technical UUID (FASTEST - use when you have UUID).

        Args:
            entity_id: Technical UUID
            entity: Updated entity data
            entity_class: Entity class/model name
            transition: Optional workflow transition name
            entity_version: Entity model version

        Returns:
            EntityResponse with updated entity and metadata
        """
        try:
            additional_meta = {}
            if transition:
                additional_meta["update_transition"] = transition

            meta = await self._get_repository_meta("", entity_class, entity_version, additional_meta)

            updated_id = await self._repository.update(meta, entity_id, entity)

            if not updated_id:
                raise EntityServiceError("Update operation returned no entity ID", entity_class, entity_id)

            # Add technical_id to entity data
            entity_with_id = {**entity, "technical_id": updated_id}

            # Parse entity data
            parsed_entity = self._parse_entity_data(entity_with_id, entity_class)

            # Create response
            response = self._create_entity_response(parsed_entity, updated_id)

            logger.debug(f"Updated entity {entity_id} of type {entity_class}")
            return response

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to update entity {entity_id} of type: {entity_class}")
            raise EntityServiceError(f"Update failed: {str(e)}", entity_class, entity_id)

    async def update_by_business_id(
        self,
        entity: Dict[str, Any],
        business_id_field: str,
        entity_class: str,
        transition: Optional[str] = None,
        entity_version: str = "1.0"
    ) -> EntityResponse:
        """
        Update existing entity by business identifier (MEDIUM SPEED).

        Args:
            entity: Updated entity data (must contain business ID)
            business_id_field: Field name containing the business ID
            entity_class: Entity class/model name
            transition: Optional workflow transition name
            entity_version: Entity model version

        Returns:
            EntityResponse with updated entity and metadata
        """
        try:
            business_id = entity.get(business_id_field)
            if not business_id:
                raise EntityServiceError(f"Entity data missing required field: {business_id_field}", entity_class)

            # Find existing entity
            existing = await self.find_by_business_id(entity_class, business_id, business_id_field, entity_version)
            if not existing:
                raise EntityServiceError(f"Entity not found with {business_id_field}={business_id}", entity_class, business_id)

            # Update using technical ID
            return await self.update(existing.get_id(), entity, entity_class, transition, entity_version)

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to update entity by business ID: {entity.get(business_id_field)}")
            raise EntityServiceError(f"Update by business ID failed: {str(e)}", entity_class)

    async def delete_by_id(self, entity_id: str, entity_class: str, entity_version: str = "1.0") -> str:
        """
        Delete entity by technical UUID (FASTEST).

        Args:
            entity_id: Technical UUID to delete
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            UUID of deleted entity
        """
        try:
            meta = await self._get_repository_meta("", entity_class, entity_version)

            await self._repository.delete_by_id(meta, entity_id)

            logger.debug(f"Deleted entity {entity_id} of type {entity_class}")
            return entity_id

        except Exception as e:
            logger.exception(f"Failed to delete entity {entity_id} of type: {entity_class}")
            raise EntityServiceError(f"Delete failed: {str(e)}", entity_class, entity_id)

    async def delete_by_business_id(
        self,
        entity_class: str,
        business_id: str,
        business_id_field: str,
        entity_version: str = "1.0"
    ) -> bool:
        """
        Delete entity by business identifier.

        Args:
            entity_class: Entity class/model name
            business_id: Business identifier value
            business_id_field: Field name containing the business ID
            entity_version: Entity model version

        Returns:
            True if deleted, False if not found
        """
        try:
            # Find existing entity
            existing = await self.find_by_business_id(entity_class, business_id, business_id_field, entity_version)
            if not existing:
                return False

            # Delete using technical ID
            await self.delete_by_id(existing.get_id(), entity_class, entity_version)
            return True

        except Exception as e:
            logger.exception(f"Failed to delete entity by business ID: {business_id}")
            raise EntityServiceError(f"Delete by business ID failed: {str(e)}", entity_class, business_id)

    # ========================================
    # BATCH OPERATIONS
    # ========================================

    async def save_all(
        self,
        entities: List[Dict[str, Any]],
        entity_class: str,
        entity_version: str = "1.0"
    ) -> List[EntityResponse]:
        """
        Save multiple entities in batch.

        Args:
            entities: List of entities to save
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            List of EntityResponse with saved entities and metadata
        """
        try:
            if not entities:
                return []

            meta = await self._get_repository_meta("", entity_class, entity_version)

            # Use repository batch save if available, otherwise save individually
            if hasattr(self._repository, 'save_all'):
                entity_id = await self._repository.save_all(meta, entities)
                # For batch operations, we might only get the first ID
                results = []
                for i, entity in enumerate(entities):
                    # Generate or use returned ID
                    current_id = f"{entity_id}_{i}" if entity_id else f"batch_{i}"
                    entity_with_id = {**entity, "technical_id": current_id}
                    parsed_entity = self._parse_entity_data(entity_with_id, entity_class)
                    response = self._create_entity_response(parsed_entity, current_id, "active")
                    results.append(response)
                return results
            else:
                # Save individually
                results = []
                for entity in entities:
                    result = await self.save(entity, entity_class, entity_version)
                    results.append(result)
                return results

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to save batch of {len(entities)} entities of type: {entity_class}")
            raise EntityServiceError(f"Batch save failed: {str(e)}", entity_class)

    async def delete_all(self, entity_class: str, entity_version: str = "1.0") -> int:
        """
        Delete all entities of a type (DANGEROUS - use with caution).

        Args:
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            Number of entities deleted
        """
        try:
            # First count existing entities
            existing_entities = await self.find_all(entity_class, entity_version)
            count = len(existing_entities)

            if count == 0:
                return 0

            meta = await self._get_repository_meta("", entity_class, entity_version)
            await self._repository.delete_all(meta)

            logger.warning(f"Deleted ALL {count} entities of type {entity_class}")
            return count

        except Exception as e:
            logger.exception(f"Failed to delete all entities of type: {entity_class}")
            raise EntityServiceError(f"Delete all failed: {str(e)}", entity_class)

    # ========================================
    # WORKFLOW AND TRANSITION METHODS
    # ========================================

    async def get_transitions(self, entity_id: str, entity_class: str, entity_version: str = "1.0") -> List[str]:
        """
        Get available transitions for an entity.

        Args:
            entity_id: Technical UUID of the entity
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            List of available transition names
        """
        try:
            meta = await self._get_repository_meta("", entity_class, entity_version)

            if hasattr(self._repository, 'get_transitions'):
                transitions = await self._repository.get_transitions(meta, entity_id)
                if isinstance(transitions, list):
                    return transitions
                elif isinstance(transitions, dict):
                    return list(transitions.keys())
                else:
                    return []
            else:
                # Return default transitions if repository doesn't support it
                return ["update", "complete", "cancel"]

        except Exception as e:
            logger.exception(f"Failed to get transitions for entity {entity_id}")
            raise EntityServiceError(f"Get transitions failed: {str(e)}", entity_class, entity_id)

    async def execute_transition(
        self,
        entity_id: str,
        transition: str,
        entity_class: str,
        entity_version: str = "1.0"
    ) -> EntityResponse:
        """
        Execute a workflow transition on an entity.

        Args:
            entity_id: Technical UUID of the entity
            transition: Transition name to execute
            entity_class: Entity class/model name
            entity_version: Entity model version

        Returns:
            EntityResponse with updated entity and metadata
        """
        try:
            # Get current entity
            current_entity = await self.get_by_id(entity_id, entity_class, entity_version)
            if not current_entity:
                raise EntityServiceError(f"Entity not found: {entity_id}", entity_class, entity_id)

            # Execute transition by updating with transition
            return await self.update(entity_id, current_entity.data, entity_class, transition, entity_version)

        except EntityServiceError:
            raise
        except Exception as e:
            logger.exception(f"Failed to execute transition {transition} on entity {entity_id}")
            raise EntityServiceError(f"Execute transition failed: {str(e)}", entity_class, entity_id)

    # ========================================
    # LEGACY COMPATIBILITY METHODS
    # ========================================

    async def get_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, meta=None) -> Any:
        """
        @deprecated Use get_by_id() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("get_item() is deprecated, use get_by_id() instead", DeprecationWarning, stacklevel=2)

        try:
            result = await self.get_by_id(technical_id, entity_model, entity_version)
            return result.data if result else None
        except EntityServiceError:
            return None
        except Exception as e:
            logger.exception(f"Legacy get_item failed: {e}")
            return None

    async def get_items(self, token: str, entity_model: str, entity_version: str) -> List[Any]:
        """
        @deprecated Use find_all() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("get_items() is deprecated, use find_all() instead", DeprecationWarning, stacklevel=2)

        try:
            results = await self.find_all(entity_model, entity_version)
            return [result.data for result in results]
        except EntityServiceError:
            return []
        except Exception as e:
            logger.exception(f"Legacy get_items failed: {e}")
            return []

    async def get_single_item_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> Any:
        """
        @deprecated Use search() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("get_single_item_by_condition() is deprecated, use search() instead", DeprecationWarning, stacklevel=2)

        try:
            # Convert legacy condition to SearchConditionRequest
            search_request = self._convert_legacy_condition(condition)
            search_request.limit = 1

            results = await self.search(entity_model, search_request, entity_version)
            return results[0].data if results else None
        except EntityServiceError:
            return None
        except Exception as e:
            logger.exception(f"Legacy get_single_item_by_condition failed: {e}")
            return None

    async def get_items_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> List[Any]:
        """
        @deprecated Use search() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("get_items_by_condition() is deprecated, use search() instead", DeprecationWarning, stacklevel=2)

        try:
            # Handle legacy condition format
            if isinstance(condition, dict) and CHAT_REPOSITORY in condition:
                actual_condition = condition.get(CHAT_REPOSITORY)
            else:
                actual_condition = condition

            # Convert legacy condition to SearchConditionRequest
            search_request = self._convert_legacy_condition(actual_condition)

            results = await self.search(entity_model, search_request, entity_version)
            return [result.data for result in results]
        except EntityServiceError:
            return []
        except Exception as e:
            logger.exception(f"Legacy get_items_by_condition failed: {e}")
            return []

    async def add_item(self, token: str, entity_model: str, entity_version: str, entity: Any, meta: Any = None) -> Any:
        """
        @deprecated Use save() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("add_item() is deprecated, use save() instead", DeprecationWarning, stacklevel=2)

        try:
            result = await self.save(entity, entity_model, entity_version)
            return result.get_id()
        except EntityServiceError:
            return None
        except Exception as e:
            logger.exception(f"Legacy add_item failed: {e}")
            return None

    async def update_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, entity: Any, meta: Any) -> Any:
        """
        @deprecated Use update() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("update_item() is deprecated, use update() instead", DeprecationWarning, stacklevel=2)

        try:
            transition = meta.get("update_transition") if isinstance(meta, dict) else None
            result = await self.update(technical_id, entity, entity_model, transition, entity_version)
            return result.get_id()
        except EntityServiceError:
            return None
        except Exception as e:
            logger.exception(f"Legacy update_item failed: {e}")
            return None

    async def delete_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, meta: Any) -> Any:
        """
        @deprecated Use delete_by_id() instead for better clarity

        Legacy method for backward compatibility.
        """
        import warnings
        warnings.warn("delete_item() is deprecated, use delete_by_id() instead", DeprecationWarning, stacklevel=2)

        try:
            return await self.delete_by_id(technical_id, entity_model, entity_version)
        except EntityServiceError:
            return None
        except Exception as e:
            logger.exception(f"Legacy delete_item failed: {e}")
            return None

    def _convert_legacy_condition(self, condition: Any) -> SearchConditionRequest:
        """
        Convert legacy condition format to SearchConditionRequest.

        Args:
            condition: Legacy condition format

        Returns:
            SearchConditionRequest object
        """
        builder = SearchConditionRequest.builder()

        if isinstance(condition, dict):
            for key, value in condition.items():
                builder.equals(key, value)
        elif isinstance(condition, str):
            # Assume it's a simple string condition
            builder.equals("name", condition)

        return builder.build()

    # Keep the original _find_by_criteria for internal use
    async def _find_by_criteria(self, token, entity_model, entity_version, condition):
        """Internal method for legacy compatibility."""
        try:
            search_request = self._convert_legacy_condition(condition)
            results = await self.search(entity_model, search_request, entity_version)
            return [result.data for result in results]
        except Exception as e:
            logger.exception(f"Internal _find_by_criteria failed: {e}")
            return []

    async def get_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, meta = None) -> Any:
        """Retrieve a single item based on its ID."""
        repository_meta = await self._repository.get_meta(token, entity_model, entity_version)
        if meta:
            repository_meta.update(meta)
        resp = await self._repository.find_by_id(meta, technical_id)
        if resp and isinstance(resp, dict) and resp.get("errorMessage"):
            return []
        if entity_model:
            model_cls = self._model_registry.get(entity_model.lower())
            resp = parse_entity(model_cls, resp)
        return resp

    async def get_items(self, token: str, entity_model: str, entity_version: str) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        meta = await self._repository.get_meta(token, entity_model, entity_version)
        resp = await self._repository.find_all(meta)
        if resp and isinstance(resp, dict) and resp.get("errorMessage"):
            return []
        model_cls = self._model_registry.get(entity_model.lower())
        resp = parse_entity(model_cls, resp)
        return resp

    async def get_single_item_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        resp = await self._find_by_criteria(token, entity_model, entity_version, condition)
        if resp and isinstance(resp, dict) and resp.get("errorMessage"):
            return []
        model_cls = self._model_registry.get(entity_model.lower())
        resp = parse_entity(model_cls, resp)
        return resp

    async def get_items_by_condition(self, token: str, entity_model: str, entity_version: str, condition: Any) -> List[Any]:
        """Retrieve multiple items based on their IDs."""
        resp = await self._find_by_criteria(token, entity_model, entity_version, condition.get(CHAT_REPOSITORY))
        if resp and isinstance(resp, dict) and resp.get("errorMessage"):
            return []
        model_cls = self._model_registry.get(entity_model.lower())
        resp = parse_entity(model_cls, resp)
        return resp

    async def add_item(self, token: str, entity_model: str, entity_version: str, entity: Any, meta: Any = None) -> Any:
        """Add a new item to the repository."""
        repository_meta = await self._repository.get_meta(token, entity_model, entity_version)
        if meta:
            repository_meta.update(meta)
        resp = await self._repository.save(repository_meta, entity)
        return resp

    async def update_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, entity: Any, meta: Any) -> Any:
        """Update an existing item in the repository."""
        repository_meta = await self._repository.get_meta(token, entity_model, entity_version)
        meta.update(repository_meta)
        resp = await self._repository.update(meta=meta, technical_id=technical_id, entity=entity)
        return resp

    async def _find_by_criteria(self, token, entity_model, entity_version, condition):
        meta = await self._repository.get_meta(token, entity_model, entity_version)
        resp = await self._repository.find_all_by_criteria(meta, condition)
        model_cls = self._model_registry.get(entity_model.lower())
        resp = parse_entity(model_cls, resp)
        return resp

    async def delete_item(self, token: str, entity_model: str, entity_version: str, technical_id: str, meta: Any) -> Any:
        """Update an existing item in the repository."""
        repository_meta = await self._repository.get_meta(token, entity_model, entity_version)
        meta.update(repository_meta)
        resp = await self._repository.delete_by_id(meta, technical_id)
        return resp

    async def get_transitions(self, token: str, technical_id: str, meta: Any) -> Any:
        """Get next transitions"""
        resp = await self._repository.get_transitions(meta=meta, technical_id=technical_id)
        return resp