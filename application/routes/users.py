"""
User Routes for Cyoda Client Application

Manages all User-related API endpoints including CRUD operations
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

# Import User entity and models
from application.entity.user.version_1.user import User
from application.models.user_models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    UserListResponse,
    UserQueryParams,
    UserResponse,
    UserSearchResponse,
    UserUpdateQueryParams,
    ValidationErrorResponse,
)
from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service


# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# ---- Routes -----------------------------------------------------------------


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
    """Create a new User account with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity (will trigger register_user transition automatically)
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

        if query_args.email:
            search_conditions["email"] = query_args.email

        if query_args.active is not None:
            search_conditions["active"] = str(query_args.active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.timezone:
            search_conditions["timezone"] = query_args.timezone

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

        return jsonify({"users": paginated_entities, "total": len(entity_list)}), 200

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
        logger.warning("Validation error updating User %s: %s", entity_id, str(e))
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


# ---- Additional Entity Service Endpoints ----------------------------------------


@users_bp.route("/by-email/<email>", methods=["GET"])
@tag(["users"])
@operation_id("get_user_by_email")
@validate(
    responses={
        200: (UserResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_email(email: str) -> ResponseReturnValue:
    """Get User by email address"""
    try:
        result = await service.find_by_business_id(
            entity_class=User.ENTITY_NAME,
            business_id=email.lower(),
            business_id_field="email",
            entity_version=str(User.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "User not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception("Error getting User by email %s: %s", email, str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["users"])
@operation_id("check_user_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if User exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking User existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@users_bp.route("/count", methods=["GET"])
@tag(["users"])
@operation_id("count_users")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Users"""
    try:
        count = await service.count(
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Users: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["users"])
@operation_id("get_user_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for User"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error getting transitions for User %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@users_bp.route("/search", methods=["POST"])
@tag(["users"])
@operation_id("search_users")
@validate(
    request=SearchRequest,
    responses={
        200: (UserSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Users using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            if field == "active":
                builder.equals(field, str(value).lower())
            else:
                builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=User.ENTITY_NAME,
            condition=search_request,
            entity_version=str(User.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"users": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Users: %s", str(e))
        return {"error": str(e)}, 500


@users_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["users"])
@operation_id("trigger_user_transition")
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
    """Trigger a specific workflow transition with validation"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "User not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on User %s", data.transition_name, entity_id
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previous_state": previous_state,
                    "new_state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error executing transition on User %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
