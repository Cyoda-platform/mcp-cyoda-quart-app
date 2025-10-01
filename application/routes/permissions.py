"""
Permission Routes for Cyoda Client Application

Manages all Permission-related API endpoints including CRUD operations
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

# Import entity and models
from application.entity.permission.version_1.permission import Permission
from application.models.request_models import (
    PermissionQueryParams,
    PermissionUpdateQueryParams,
    SearchRequest,
)
from application.models.response_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    PermissionListResponse,
    PermissionResponse,
    PermissionSearchResponse,
    ValidationErrorResponse,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


permissions_bp = Blueprint("permissions", __name__, url_prefix="/api/permissions")


@permissions_bp.route("", methods=["POST"])
@tag(["permissions"])
@operation_id("create_permission")
@validate(
    request=Permission,
    responses={
        201: (PermissionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_permission(data: Permission) -> ResponseReturnValue:
    """Create a new Permission"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Permission.ENTITY_NAME,
            entity_version=str(Permission.ENTITY_VERSION),
        )
        logger.info("Created Permission with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Permission: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Permission: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@permissions_bp.route("/<entity_id>", methods=["GET"])
@tag(["permissions"])
@operation_id("get_permission")
@validate(
    responses={
        200: (PermissionResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_permission(entity_id: str) -> ResponseReturnValue:
    """Get Permission by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Permission.ENTITY_NAME,
            entity_version=str(Permission.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Permission not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Permission %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@permissions_bp.route("", methods=["GET"])
@validate_querystring(PermissionQueryParams)
@tag(["permissions"])
@operation_id("list_permissions")
@validate(
    responses={
        200: (PermissionListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_permissions(query_args: PermissionQueryParams) -> ResponseReturnValue:
    """List Permissions with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.name:
            search_conditions["name"] = query_args.name
        if query_args.resource:
            search_conditions["resource"] = query_args.resource
        if query_args.action:
            search_conditions["action"] = query_args.action
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
                entity_class=Permission.ENTITY_NAME,
                condition=condition,
                entity_version=str(Permission.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Permission.ENTITY_NAME,
                entity_version=str(Permission.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Permissions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@permissions_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PermissionUpdateQueryParams)
@tag(["permissions"])
@operation_id("update_permission")
@validate(
    request=Permission,
    responses={
        200: (PermissionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_permission(
    entity_id: str, data: Permission, query_args: PermissionUpdateQueryParams
) -> ResponseReturnValue:
    """Update Permission and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Permission.ENTITY_NAME,
            transition=transition,
            entity_version=str(Permission.ENTITY_VERSION),
        )

        logger.info("Updated Permission %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Permission %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Permission %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@permissions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["permissions"])
@operation_id("delete_permission")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_permission(entity_id: str) -> ResponseReturnValue:
    """Delete Permission"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Permission.ENTITY_NAME,
            entity_version=str(Permission.ENTITY_VERSION),
        )

        logger.info("Deleted Permission %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Permission deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Permission %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@permissions_bp.route("/count", methods=["GET"])
@tag(["permissions"])
@operation_id("count_permissions")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Permissions"""
    try:
        count = await service.count(
            entity_class=Permission.ENTITY_NAME,
            entity_version=str(Permission.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Permissions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@permissions_bp.route("/search", methods=["POST"])
@tag(["permissions"])
@operation_id("search_permissions")
@validate(
    request=SearchRequest,
    responses={
        200: (PermissionSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Permissions"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)
        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Permission.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Permission.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200
    except Exception as e:
        logger.exception("Error searching Permissions: %s", str(e))
        return {"error": str(e)}, 500
