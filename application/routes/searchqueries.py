"""
SearchQuery Routes for Cyoda Client Application

Manages all SearchQuery-related API endpoints including CRUD operations
and search execution operations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.searchquery.version_1.searchquery import SearchQuery
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Request/Response Models
class SearchQueryQueryParams(BaseModel):
    """Query parameters for listing SearchQueries"""

    query_text: Optional[str] = Field(None, description="Filter by query text")
    sort_order: Optional[str] = Field(None, description="Filter by sort order")
    limit: int = Field(10, description="Number of queries to return", ge=1, le=100)
    offset: int = Field(0, description="Number of queries to skip", ge=0)


class SearchQueryUpdateQueryParams(BaseModel):
    """Query parameters for updating SearchQueries"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class SearchQueryExecuteRequest(BaseModel):
    """Request model for executing a search query"""

    query_text: str = Field(..., description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    include_hierarchy: bool = Field(False, description="Include parent hierarchy")
    sort_order: str = Field("relevance", description="Sort order")
    limit: int = Field(10, description="Number of results", ge=1, le=100)
    offset: int = Field(0, description="Result offset", ge=0)
    search_fields: Optional[List[str]] = Field(None, description="Fields to search in")


class SearchQueryResponse(BaseModel):
    """Response model for single SearchQuery"""

    id: str = Field(..., description="Entity ID")
    status: str = Field(..., description="Operation status")
    transition: Optional[str] = Field(None, description="Applied transition")


class SearchQueryListResponse(BaseModel):
    """Response model for SearchQuery list"""

    queries: List[Dict[str, Any]] = Field(..., description="List of search queries")
    total: int = Field(..., description="Total number of queries")


class SearchQueryExecuteResponse(BaseModel):
    """Response model for search execution"""

    query_id: str = Field(..., description="Search query ID")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    execution_time_ms: Optional[int] = Field(None, description="Execution time")
    query_text: str = Field(..., description="Original query text")


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


searchqueries_bp = Blueprint("searchqueries", __name__, url_prefix="/searchquery")


# ---- Core CRUD Routes -------------------------------------------------------


@searchqueries_bp.route("", methods=["POST"])
@tag(["searchqueries"])
@operation_id("create_searchquery")
@validate(
    request=SearchQuery,
    responses={
        201: (SearchQueryResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def create_searchquery(data: SearchQuery) -> ResponseReturnValue:
    """Create a new SearchQuery"""
    try:
        # Get optional transition from query params
        transition = request.args.get("transition")

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True, exclude_none=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Apply transition if specified
        if transition:
            await service.execute_transition(
                entity_id=response.metadata.id,
                transition=transition,
                entity_class=SearchQuery.ENTITY_NAME,
                entity_version=str(SearchQuery.ENTITY_VERSION),
            )

        logger.info("Created SearchQuery with ID: %s", response.metadata.id)

        return {
            "id": response.metadata.id,
            "status": "created",
            "transition": transition,
        }, 201

    except ValueError as e:
        logger.warning("Validation error creating SearchQuery: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating SearchQuery: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@searchqueries_bp.route("/<entity_id>", methods=["GET"])
@tag(["searchqueries"])
@operation_id("get_searchquery")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_searchquery(entity_id: str) -> ResponseReturnValue:
    """Get SearchQuery by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        if not response:
            return {"error": "SearchQuery not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting SearchQuery %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@searchqueries_bp.route("", methods=["GET"])
@validate_querystring(SearchQueryQueryParams)
@tag(["searchqueries"])
@operation_id("list_searchqueries")
@validate(
    responses={
        200: (SearchQueryListResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def list_searchqueries(query_args: SearchQueryQueryParams) -> ResponseReturnValue:
    """List SearchQueries with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.query_text:
            search_conditions["query_text"] = query_args.query_text
        if query_args.sort_order:
            search_conditions["sort_order"] = query_args.sort_order

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=SearchQuery.ENTITY_NAME,
                condition=condition,
                entity_version=str(SearchQuery.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=SearchQuery.ENTITY_NAME,
                entity_version=str(SearchQuery.ENTITY_VERSION),
            )

        # Convert to list
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"queries": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing SearchQueries: %s", str(e))
        return {"error": str(e)}, 500


@searchqueries_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(SearchQueryUpdateQueryParams)
@tag(["searchqueries"])
@operation_id("update_searchquery")
@validate(
    request=SearchQuery,
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def update_searchquery(
    entity_id: str, data: SearchQuery, query_args: SearchQueryUpdateQueryParams
) -> ResponseReturnValue:
    """Update SearchQuery and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True, exclude_none=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=SearchQuery.ENTITY_NAME,
            transition=query_args.transition,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        logger.info("Updated SearchQuery %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating SearchQuery %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating SearchQuery %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@searchqueries_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["searchqueries"])
@operation_id("delete_searchquery")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def delete_searchquery(entity_id: str) -> ResponseReturnValue:
    """Delete SearchQuery"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        logger.info("Deleted SearchQuery %s", entity_id)

        return {
            "success": True,
            "message": "SearchQuery deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting SearchQuery %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Search Execution Operations ---------------------------------------------


@searchqueries_bp.route("/execute", methods=["POST"])
@tag(["searchqueries"])
@operation_id("execute_search")
@validate(
    request=SearchQueryExecuteRequest,
    responses={
        200: (SearchQueryExecuteResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def execute_search(data: SearchQueryExecuteRequest) -> ResponseReturnValue:
    """Execute a search query and return results"""
    try:
        # Create SearchQuery entity
        search_query = SearchQuery(
            query_text=data.query_text,
            filters=data.filters or {},
            include_hierarchy=data.include_hierarchy,
            sort_order=data.sort_order,
            limit=data.limit,
            offset=data.offset,
            search_fields=data.search_fields or ["title", "text"],
        )

        search_data = search_query.model_dump(by_alias=True, exclude_none=True)

        # Save the search query
        response = await service.save(
            entity=search_data,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Execute search workflow
        await service.execute_transition(
            entity_id=response.metadata.id,
            transition="execute_search",
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Get updated search results
        updated_response = await service.get_by_id(
            entity_id=response.metadata.id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        search_result = _to_entity_dict(updated_response.data)

        return {
            "query_id": response.metadata.id,
            "results": search_result.get("results", []),
            "total": search_result.get("result_count", 0),
            "execution_time_ms": search_result.get("execution_time_ms"),
            "query_text": data.query_text,
        }, 200

    except Exception as e:
        logger.exception("Error executing search: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@searchqueries_bp.route("/<entity_id>/execute", methods=["POST"])
@tag(["searchqueries"])
@operation_id("execute_existing_search")
@validate(
    responses={
        200: (SearchQueryExecuteResponse, None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def execute_existing_search(entity_id: str) -> ResponseReturnValue:
    """Execute an existing SearchQuery"""
    try:
        # Execute search workflow
        await service.execute_transition(
            entity_id=entity_id,
            transition="execute_search",
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Get updated search results
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        if not response:
            return {"error": "SearchQuery not found", "code": "NOT_FOUND"}, 404

        search_result = _to_entity_dict(response.data)

        return {
            "query_id": entity_id,
            "results": search_result.get("results", []),
            "total": search_result.get("result_count", 0),
            "execution_time_ms": search_result.get("execution_time_ms"),
            "query_text": search_result.get("query_text", ""),
        }, 200

    except Exception as e:
        logger.exception("Error executing existing search %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@searchqueries_bp.route("/<entity_id>/results", methods=["GET"])
@tag(["searchqueries"])
@operation_id("get_search_results")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_search_results(entity_id: str) -> ResponseReturnValue:
    """Get results from a previously executed SearchQuery"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        if not response:
            return {"error": "SearchQuery not found", "code": "NOT_FOUND"}, 404

        search_result = _to_entity_dict(response.data)

        return {
            "query_id": entity_id,
            "query_text": search_result.get("query_text", ""),
            "results": search_result.get("results", []),
            "total": search_result.get("result_count", 0),
            "execution_time_ms": search_result.get("execution_time_ms"),
            "executed_at": search_result.get("executed_at"),
            "state": search_result.get("state"),
        }, 200

    except Exception as e:
        logger.exception("Error getting search results %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
