"""
SearchQuery Routes for Cyoda Client Application

Manages all SearchQuery-related API endpoints including search execution
and caching as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import tag

from application.entity.searchquery.version_1.searchquery import SearchQuery
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


searchquery_bp = Blueprint("searchquery", __name__, url_prefix="/api/searchquery")


@searchquery_bp.route("", methods=["POST"])
@tag(["searchquery"])
async def execute_search() -> ResponseReturnValue:
    """Execute a search query"""
    try:
        data = await request.get_json()

        # Extract transition if provided
        transition = data.get("transition")
        search_data = data.get("data", data)

        # Create SearchQuery instance for validation
        search_query = SearchQuery(**search_data)

        # Convert to dict for entity service
        entity_data = search_query.model_dump(by_alias=True)

        # Get entity service
        service = get_entity_service()

        # Save the entity
        if transition:
            response = await service.save(
                entity=entity_data,
                entity_class=SearchQuery.ENTITY_NAME,
                entity_version=str(SearchQuery.ENTITY_VERSION),
                transition=transition,
            )
        else:
            response = await service.save(
                entity=entity_data,
                entity_class=SearchQuery.ENTITY_NAME,
                entity_version=str(SearchQuery.ENTITY_VERSION),
            )

        logger.info("Created SearchQuery with ID: %s", response.metadata.id)

        # Get the saved search query data
        search_result_data = _to_entity_dict(response.data)

        # Return search results if available
        result = {
            "id": response.metadata.id,
            "results": search_result_data.get("results", []),
            "metadata": {
                "total_results": search_result_data.get("resultsCount", 0),
                "execution_time": search_result_data.get("executionTime"),
                "cached": search_result_data.get("cachedAt") is not None,
                "query_text": search_result_data.get("queryText"),
                "filters": search_result_data.get("filters", {}),
                "state": response.metadata.state,
            },
        }

        return jsonify(result), 201

    except ValueError as e:
        logger.warning("Validation error creating SearchQuery: %s", str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error creating SearchQuery: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@searchquery_bp.route("/<entity_id>", methods=["GET"])
@tag(["searchquery"])
async def get_search_results(entity_id: str) -> ResponseReturnValue:
    """Get search query results and status"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "SearchQuery not found", "code": "NOT_FOUND"}), 404

        # Get search query data
        search_data = _to_entity_dict(response.data)

        # Return the search data with metadata
        result = {
            "id": response.metadata.id,
            "data": {
                "query_text": search_data.get("queryText"),
                "results_count": search_data.get("resultsCount", 0),
                "execution_time": search_data.get("executionTime"),
                "executed_at": search_data.get("executedAt"),
                "cached_at": search_data.get("cachedAt"),
                "filters": search_data.get("filters", {}),
                "sort_by": search_data.get("sortBy"),
                "limit": search_data.get("limit"),
                "offset": search_data.get("offset"),
            },
            "results": search_data.get("results", []),
            "meta": {
                "state": response.metadata.state,
                "created_at": response.metadata.created_at,
                "updated_at": response.metadata.updated_at,
                "cached": search_data.get("cachedAt") is not None,
                "cache_expired": search_data.get("cachedAt")
                and SearchQuery(**search_data).is_cache_expired(),
            },
        }

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Error getting SearchQuery %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@searchquery_bp.route("/cached", methods=["GET"])
@tag(["searchquery"])
async def get_cached_results() -> ResponseReturnValue:
    """Get cached search results by query hash"""
    try:
        query_hash = request.args.get("query_hash")
        include_results = request.args.get("include_results", "true").lower() == "true"

        if not query_hash:
            return (
                jsonify({"error": "Query hash is required", "code": "MISSING_HASH"}),
                400,
            )

        service = get_entity_service()

        # Search for cached queries by cache key
        from common.service.entity_service import SearchConditionRequest

        builder = SearchConditionRequest.builder()
        builder.equals("cacheKey", query_hash)
        builder.equals("state", "cached")

        search_request = builder.build()
        results = await service.search(
            entity_class=SearchQuery.ENTITY_NAME,
            condition=search_request,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        if not results:
            return (
                jsonify({"error": "No cached results found", "code": "NOT_FOUND"}),
                404,
            )

        # Get the first (most recent) cached result
        cached_result = results[0]
        search_data = _to_entity_dict(cached_result.data)

        # Check if cache is expired
        search_query = SearchQuery(**search_data)
        if search_query.is_cache_expired():
            return (
                jsonify(
                    {"error": "Cached results have expired", "code": "CACHE_EXPIRED"}
                ),
                410,
            )

        # Return cached data
        result = {
            "id": cached_result.metadata.id,
            "query_hash": query_hash,
            "cached_at": search_data.get("cachedAt"),
            "cache_ttl": search_data.get("cacheTtl"),
            "metadata": {
                "query_text": search_data.get("queryText"),
                "results_count": search_data.get("resultsCount", 0),
                "execution_time": search_data.get("executionTime"),
                "filters": search_data.get("filters", {}),
                "sort_by": search_data.get("sortBy"),
                "limit": search_data.get("limit"),
                "offset": search_data.get("offset"),
            },
        }

        # Include results if requested
        if include_results:
            result["results"] = search_data.get("results", [])

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Error getting cached search results: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@searchquery_bp.route("/<entity_id>", methods=["PUT"])
@tag(["searchquery"])
async def update_search_query(entity_id: str) -> ResponseReturnValue:
    """Update search query and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        data = await request.get_json()
        transition = request.args.get("transition")

        # Create SearchQuery instance for validation
        search_query = SearchQuery(**data)

        # Convert to dict for entity service
        entity_data = search_query.model_dump(by_alias=True)

        service = get_entity_service()

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=SearchQuery.ENTITY_NAME,
            transition=transition,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        logger.info("Updated SearchQuery %s", entity_id)

        return jsonify(_to_entity_dict(response.data)), 200

    except Exception as e:
        logger.exception("Error updating SearchQuery %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@searchquery_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["searchquery"])
async def trigger_search_transition(entity_id: str) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        data = await request.get_json()
        transition_name = data.get("transition_name")

        if not transition_name:
            return (
                jsonify(
                    {
                        "error": "Transition name is required",
                        "code": "MISSING_TRANSITION",
                    }
                ),
                400,
            )

        service = get_entity_service()

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=transition_name,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on SearchQuery %s", transition_name, entity_id
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "transition": transition_name,
                    "new_state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error executing transition on SearchQuery %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500
