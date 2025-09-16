"""
User Routes for Purrfect Pets API

Manages all User-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.user.version_1.user import User
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
@tag(["users"])
@operation_id("get_users")
async def get_users() -> ResponseReturnValue:
    """Get all users (admin only)"""
    try:
        service = get_entity_service()

        entities = await service.find_all(
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        # Convert to response format (exclude sensitive data)
        users_data = []
        for entity_response in entities:
            user_data = _to_entity_dict(entity_response.data)
            # Remove password from response
            user_data.pop("password", None)
            user_data["status"] = entity_response.metadata.state
            users_data.append(user_data)

        return jsonify(users_data), 200

    except Exception as e:
        logger.exception("Error getting users: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["GET"])
@tag(["users"])
@operation_id("get_user")
async def get_user(user_id: str) -> ResponseReturnValue:
    """Get user by ID"""
    try:
        service = get_entity_service()

        response = await service.get_by_id(
            entity_id=user_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "User not found"}), 404

        user_data = _to_entity_dict(response.data)
        # Remove password from response
        user_data.pop("password", None)
        user_data["status"] = response.metadata.state

        return jsonify(user_data), 200

    except Exception as e:
        logger.exception("Error getting user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("", methods=["POST"])
@tag(["users"])
@operation_id("create_user")
async def create_user() -> ResponseReturnValue:
    """Create new user"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Create User entity from request data
        user = User(**data)
        entity_data = user.model_dump(by_alias=True)

        # Save the entity (will trigger automatic transition to active)
        response = await service.save(
            entity=entity_data,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Created User with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "username": user.username,
                    "status": response.metadata.state,
                    "message": "User created successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        logger.warning("Validation error creating user: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error creating user: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["PUT"])
@tag(["users"])
@operation_id("update_user")
async def update_user(user_id: str) -> ResponseReturnValue:
    """Update user"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Map transition names to workflow transition names
        transition_map = {
            "activate": "transition_to_active",
            "deactivate": "transition_to_inactive",
            "suspend": "transition_to_suspended",
        }

        workflow_transition = None
        if transition:
            workflow_transition = transition_map.get(transition)
            if not workflow_transition:
                return jsonify({"error": f"Invalid transition: {transition}"}), 400

        # Create User entity from request data for validation
        user = User(**data)
        entity_data = user.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=user_id,
            entity=entity_data,
            entity_class=User.ENTITY_NAME,
            transition=workflow_transition,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Updated User %s", user_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "username": user.username,
                    "status": response.metadata.state,
                    "message": f"User updated{' and ' + transition if transition else ''} successfully",
                }
            ),
            200,
        )

    except ValueError as e:
        logger.warning("Validation error updating user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error updating user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["DELETE"])
@tag(["users"])
@operation_id("delete_user")
async def delete_user(user_id: str) -> ResponseReturnValue:
    """Delete user"""
    try:
        service = get_entity_service()

        await service.delete_by_id(
            entity_id=user_id,
            entity_class=User.ENTITY_NAME,
            entity_version=str(User.ENTITY_VERSION),
        )

        logger.info("Deleted User %s", user_id)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User deleted successfully",
                    "entity_id": user_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error deleting user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 500
