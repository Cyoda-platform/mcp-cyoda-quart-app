"""
Category Routes for Cyoda Client Application

Manages all Category-related API endpoints including CRUD operations
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

from ..entity.category.version_1.category import Category
from ..models import (
    CategoryListResponse,
    CategoryQueryParams,
    CategoryResponse,
    CategoryUpdateQueryParams,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.route("", methods=["POST"])
@tag(["categories"])
@operation_id("create_category")
@validate(
    request=Category,
    responses={
        201: (CategoryResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_category(data: Category) -> ResponseReturnValue:
    """Create a new Category"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        logger.info("Created Category with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Category: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Category: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@categories_bp.route("/<entity_id>", methods=["GET"])
@tag(["categories"])
@operation_id("get_category")
@validate(
    responses={
        200: (CategoryResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_category(entity_id: str) -> ResponseReturnValue:
    """Get Category by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Category not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Category %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@categories_bp.route("", methods=["GET"])
@validate_querystring(CategoryQueryParams)
@tag(["categories"])
@operation_id("list_categories")
@validate(
    responses={
        200: (CategoryListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_categories(query_args: CategoryQueryParams) -> ResponseReturnValue:
    """List Categories with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.state:
            search_conditions["state"] = query_args.state
        if query_args.name:
            search_conditions["name"] = query_args.name

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()
            entities = await service.search(
                entity_class=Category.ENTITY_NAME,
                condition=condition,
                entity_version=str(Category.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Category.ENTITY_NAME,
                entity_version=str(Category.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Categories: %s", str(e))
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(CategoryUpdateQueryParams)
@tag(["categories"])
@operation_id("update_category")
@validate(
    request=Category,
    responses={
        200: (CategoryResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_category(
    entity_id: str, data: Category, query_args: CategoryUpdateQueryParams
) -> ResponseReturnValue:
    """Update Category and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Category.ENTITY_NAME,
            transition=transition,
            entity_version=str(Category.ENTITY_VERSION),
        )

        logger.info("Updated Category %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Category %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Category %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@categories_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["categories"])
@operation_id("delete_category")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_category(entity_id: str) -> ResponseReturnValue:
    """Delete Category"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )

        logger.info("Deleted Category %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Category deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Category %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@categories_bp.route("/count", methods=["GET"])
@tag(["categories"])
@operation_id("count_categories")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Categories"""
    try:
        count = await service.count(
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Categories: %s", str(e))
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["categories"])
@operation_id("trigger_category_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Category not found"}), 404

        previous_state = current_entity.metadata.state

        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Category %s", data.transition_name, entity_id
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception(
            "Error executing transition on Category %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
