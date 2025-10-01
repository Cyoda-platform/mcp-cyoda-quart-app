"""
User Routes for Cyoda Client Application

Manages all User-related API endpoints including CRUD operations
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

from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service

# Import entity and models
from application.entity.user.version_1.user import User
from application.models.request_models import (
    SearchRequest,
    TransitionRequest,
    UserQueryParams,
    UserUpdateQueryParams,
)
from application.models.response_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    TransitionResponse,
    TransitionsResponse,
    UserListResponse,
    UserResponse,
    UserSearchResponse,
    ValidationErrorResponse,
)

# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["POST"])
@tag(["users"])
@operation_id("create_user")
@validate(
    request=User,
    responses={
        201: (UserResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_user(data: User) -> ResponseReturnValue:
    """Create a new User with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Created User with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating User: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating User: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.route("/<entity_id>", methods=["GET"])
@tag(["users"])
@operation_id("get_user")
@validate(
    responses={
        200: (UserResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_user(entity_id: str) -> ResponseReturnValue:
    """Get User by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        if not response:
            return {"error": "User not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting User %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@users_bp.route("", methods=["GET"])
@validate_querystring(UserQueryParams)
@tag(["users"])
@operation_id("list_users")
@validate(
    responses={
        200: (UserListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_users(query_args: UserQueryParams) -> ResponseReturnValue:
    """List Users with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.username:
            search_conditions["username"] = query_args.username

        if query_args.email:
            search_conditions["email"] = query_args.email

        if query_args.is_active is not None:
            search_conditions["is_active"] = str(query_args.is_active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=User.ENTITY_NAME,
                condition=condition,
                entity_version=str(User.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=User.ENTITY_NAME,
                entity_version=str(User.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Users: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(UserUpdateQueryParams)
@tag(["users"])
@operation_id("update_user")
@validate(
    request=User,
    responses={
        200: (UserResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_user(
    entity_id: str, data: User, query_args: UserUpdateQueryParams
) -> ResponseReturnValue:
    """Update User and optionally trigger workflow transition with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=User.ENTITY_NAME,
            transition=transition,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Updated User %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating User %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating User %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@users_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["users"])
@operation_id("delete_user")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_user(entity_id: str) -> ResponseReturnValue:
    """Delete User with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Deleted User %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="User deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting User %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
