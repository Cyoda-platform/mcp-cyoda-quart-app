"""
Role Routes for Cyoda Client Application

Manages all Role-related API endpoints including CRUD operations
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
from application.entity.role.version_1.role import Role
from application.models.request_models import (
    RoleQueryParams,
    RoleUpdateQueryParams,
    SearchRequest,
)
from application.models.response_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    RoleListResponse,
    RoleResponse,
    RoleSearchResponse,
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


roles_bp = Blueprint("roles", __name__, url_prefix="/api/roles")


@roles_bp.route("", methods=["POST"])
@tag(["roles"])
@operation_id("create_role")
@validate(
    request=Role,
    responses={
        201: (RoleResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_role(data: Role) -> ResponseReturnValue:
    """Create a new Role"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Role.ENTITY_NAME,
            entity_version=str(Role.ENTITY_VERSION),
        )
        logger.info("Created Role with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Role: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Role: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@roles_bp.route("/<entity_id>", methods=["GET"])
@tag(["roles"])
@operation_id("get_role")
@validate(
    responses={
        200: (RoleResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_role(entity_id: str) -> ResponseReturnValue:
    """Get Role by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Role.ENTITY_NAME,
            entity_version=str(Role.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Role not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Role %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@roles_bp.route("", methods=["GET"])
@validate_querystring(RoleQueryParams)
@tag(["roles"])
@operation_id("list_roles")
@validate(
    responses={
        200: (RoleListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_roles(query_args: RoleQueryParams) -> ResponseReturnValue:
    """List Roles with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.name:
            search_conditions["name"] = query_args.name
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
                entity_class=Role.ENTITY_NAME,
                condition=condition,
                entity_version=str(Role.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Role.ENTITY_NAME,
                entity_version=str(Role.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Roles: %s", str(e))
        return jsonify({"error": str(e)}), 500


@roles_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(RoleUpdateQueryParams)
@tag(["roles"])
@operation_id("update_role")
@validate(
    request=Role,
    responses={
        200: (RoleResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_role(
    entity_id: str, data: Role, query_args: RoleUpdateQueryParams
) -> ResponseReturnValue:
    """Update Role and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Role.ENTITY_NAME,
            transition=transition,
            entity_version=str(Role.ENTITY_VERSION),
        )

        logger.info("Updated Role %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Role %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Role %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@roles_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["roles"])
@operation_id("delete_role")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_role(entity_id: str) -> ResponseReturnValue:
    """Delete Role"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Role.ENTITY_NAME,
            entity_version=str(Role.ENTITY_VERSION),
        )

        logger.info("Deleted Role %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Role deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Role %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@roles_bp.route("/count", methods=["GET"])
@tag(["roles"])
@operation_id("count_roles")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Roles"""
    try:
        count = await service.count(
            entity_class=Role.ENTITY_NAME,
            entity_version=str(Role.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Roles: %s", str(e))
        return jsonify({"error": str(e)}), 500


@roles_bp.route("/search", methods=["POST"])
@tag(["roles"])
@operation_id("search_roles")
@validate(
    request=SearchRequest,
    responses={
        200: (RoleSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Roles"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)
        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Role.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Role.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200
    except Exception as e:
        logger.exception("Error searching Roles: %s", str(e))
        return {"error": str(e)}, 500
