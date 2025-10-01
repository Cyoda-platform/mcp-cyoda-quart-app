"""
Position Routes for Cyoda Client Application

Manages all Position-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

# Import entity and models
from application.entity.position.version_1.position import Position
from application.models.request_models import (
    PositionQueryParams,
    PositionUpdateQueryParams,
    SearchRequest,
)
from application.models.response_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    PositionListResponse,
    PositionResponse,
    PositionSearchResponse,
    ValidationErrorResponse,
)

# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

positions_bp = Blueprint("positions", __name__, url_prefix="/api/positions")


@positions_bp.route("", methods=["POST"])
@tag(["positions"])
@operation_id("create_position")
@validate(
    request=Position,
    responses={
        201: (PositionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_position(data: Position) -> ResponseReturnValue:
    """Create a new Position"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Position.ENTITY_NAME,
            entity_version=str(Position.ENTITY_VERSION),
        )
        logger.info("Created Position with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Position: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Position: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@positions_bp.route("/<entity_id>", methods=["GET"])
@tag(["positions"])
@operation_id("get_position")
@validate(
    responses={
        200: (PositionResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_position(entity_id: str) -> ResponseReturnValue:
    """Get Position by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Position.ENTITY_NAME,
            entity_version=str(Position.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Position not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Position %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@positions_bp.route("", methods=["GET"])
@validate_querystring(PositionQueryParams)
@tag(["positions"])
@operation_id("list_positions")
@validate(
    responses={
        200: (PositionListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_positions(query_args: PositionQueryParams) -> ResponseReturnValue:
    """List Positions with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.title:
            search_conditions["title"] = query_args.title
        if query_args.department:
            search_conditions["department"] = query_args.department
        if query_args.level:
            search_conditions["level"] = query_args.level
        if query_args.is_active is not None:
            search_conditions["is_active"] = str(query_args.is_active).lower()
        if query_args.state:
            search_conditions["state"] = query_args.state

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()
            entities = await service.search(
                entity_class=Position.ENTITY_NAME,
                condition=condition,
                entity_version=str(Position.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Position.ENTITY_NAME,
                entity_version=str(Position.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Positions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PositionUpdateQueryParams)
@tag(["positions"])
@operation_id("update_position")
@validate(
    request=Position,
    responses={
        200: (PositionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_position(
    entity_id: str, data: Position, query_args: PositionUpdateQueryParams
) -> ResponseReturnValue:
    """Update Position and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Position.ENTITY_NAME,
            transition=transition,
            entity_version=str(Position.ENTITY_VERSION),
        )

        logger.info("Updated Position %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Position %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Position %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@positions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["positions"])
@operation_id("delete_position")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_position(entity_id: str) -> ResponseReturnValue:
    """Delete Position"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Position.ENTITY_NAME,
            entity_version=str(Position.ENTITY_VERSION),
        )

        logger.info("Deleted Position %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Position deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Position %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@positions_bp.route("/count", methods=["GET"])
@tag(["positions"])
@operation_id("count_positions")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Positions"""
    try:
        count = await service.count(
            entity_class=Position.ENTITY_NAME,
            entity_version=str(Position.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Positions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/search", methods=["POST"])
@tag(["positions"])
@operation_id("search_positions")
@validate(
    request=SearchRequest,
    responses={
        200: (PositionSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Positions"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)
        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Position.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Position.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200
    except Exception as e:
        logger.exception("Error searching Positions: %s", str(e))
        return {"error": str(e)}, 500
