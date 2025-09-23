"""
CatFact Routes for Cat Fact Subscription Application

Manages all CatFact-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

from ..entity.cat_fact.version_1.cat_fact import CatFact
from ..models import (
    CatFactListResponse,
    CatFactQueryParams,
    CatFactResponse,
    CatFactSearchRequest,
    CatFactSearchResponse,
    CatFactUpdateQueryParams,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    ResponseErrorResponse,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


cat_facts_bp = Blueprint("cat_facts", __name__, url_prefix="/api/cat-facts")


@cat_facts_bp.route("", methods=["POST"])
@tag(["cat-facts"])
@operation_id("create_cat_fact")
@validate(
    request=CatFact,
    responses={
        201: (CatFactResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_cat_fact(data: CatFact) -> ResponseReturnValue:
    """Create a new CatFact with comprehensive validation"""
    try:
        entity_data = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Created CatFact with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/<entity_id>", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_cat_fact")
@validate(
    responses={
        200: (CatFactResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Get CatFact by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        if not response:
            return {"error": "CatFact not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("", methods=["GET"])
@validate_querystring(CatFactQueryParams)
@tag(["cat-facts"])
@operation_id("list_cat_facts")
@validate(
    responses={
        200: (CatFactListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_cat_facts(query_args: CatFactQueryParams) -> ResponseReturnValue:
    """List CatFacts with optional filtering and validation"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.source:
            search_conditions["source"] = query_args.source

        if query_args.is_used is not None:
            search_conditions["isUsed"] = str(query_args.is_used).lower()

        if query_args.is_appropriate is not None:
            search_conditions["isAppropriate"] = str(query_args.is_appropriate).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=CatFact.ENTITY_NAME,
                condition=condition,
                entity_version=str(CatFact.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=CatFact.ENTITY_NAME,
                entity_version=str(CatFact.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(CatFactUpdateQueryParams)
@tag(["cat-facts"])
@operation_id("update_cat_fact")
@validate(
    request=CatFact,
    responses={
        200: (CatFactResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_cat_fact(
    entity_id: str, data: CatFact, query_args: CatFactUpdateQueryParams
) -> ResponseReturnValue:
    """Update CatFact and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=CatFact.ENTITY_NAME,
            transition=transition,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Updated CatFact %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@cat_facts_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["cat-facts"])
@operation_id("delete_cat_fact")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Delete CatFact with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Deleted CatFact %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="CatFact deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/available", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_available_cat_facts")
@validate(
    responses={
        200: (CatFactListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_cat_facts() -> ResponseReturnValue:
    """Get cat facts that are available for use in campaigns"""
    try:
        # Search for unused and appropriate cat facts
        builder = SearchConditionRequest.builder()
        builder.equals("isUsed", "false")
        builder.equals("isAppropriate", "true")
        condition = builder.build()

        entities = await service.search(
            entity_class=CatFact.ENTITY_NAME,
            condition=condition,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return jsonify({"entities": entity_list, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error getting available CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["cat-facts"])
@operation_id("check_cat_fact_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if CatFact exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking CatFact existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@cat_facts_bp.route("/count", methods=["GET"])
@tag(["cat-facts"])
@operation_id("count_cat_facts")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of CatFacts"""
    try:
        count = await service.count(
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/search", methods=["POST"])
@tag(["cat-facts"])
@operation_id("search_cat_facts")
@validate(
    request=CatFactSearchRequest,
    responses={
        200: (CatFactSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: CatFactSearchRequest) -> ResponseReturnValue:
    """Search CatFacts using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=CatFact.ENTITY_NAME,
            condition=search_request,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching CatFacts: %s", str(e))
        return {"error": str(e)}, 500
