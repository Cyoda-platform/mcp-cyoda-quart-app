"""
Pet Routes for Purrfect Pets API

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.pet.version_1.pet import Pet
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


pet_routes_bp = Blueprint("pets", __name__, url_prefix="/api/pets")


@pet_routes_bp.route("", methods=["GET"])
async def get_pets() -> ResponseReturnValue:
    """Get all pets with optional filtering"""
    try:
        service = get_entity_service()

        # Get query parameters
        category_id = request.args.get("category_id")
        status = request.args.get("status")
        page = int(request.args.get("page", 0))
        size = int(request.args.get("size", 20))

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if category_id:
            search_conditions["category_id"] = category_id
        if status:
            search_conditions["state"] = status

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Pet.ENTITY_NAME,
                condition=condition,
                entity_version=str(Pet.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

        # Convert to response format
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = page * size
        end = start + size
        paginated_entities = entity_list[start:end]

        return (
            jsonify(
                {
                    "content": paginated_entities,
                    "totalElements": len(entity_list),
                    "totalPages": (len(entity_list) + size - 1) // size,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error getting pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_pet(entity_id: str) -> ResponseReturnValue:
    """Get pet by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Pet ID is required"}), 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet not found"}), 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("", methods=["POST"])
async def create_pet() -> ResponseReturnValue:
    """Create new pet"""
    try:
        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Create Pet entity from request data
        pet = Pet(**data)
        entity_data = pet.model_dump(by_alias=True)

        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Created Pet with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Pet: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error creating Pet: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("/<entity_id>", methods=["PUT"])
async def update_pet(entity_id: str) -> ResponseReturnValue:
    """Update pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Pet ID is required"}), 400

        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Get transition from query parameters or request body
        transition = request.args.get("transition_name") or data.get("transition_name")

        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=Pet.ENTITY_NAME,
            transition=transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error updating Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_pet(entity_id: str) -> ResponseReturnValue:
    """Delete pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Pet ID is required"}), 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Pet deleted successfully",
                    "entity_id": entity_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("/<entity_id>/reserve", methods=["PUT"])
async def reserve_pet(entity_id: str) -> ResponseReturnValue:
    """Reserve pet for order"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Pet ID is required"}), 400

        data = await request.get_json()
        if not data or not data.get("order_id"):
            return jsonify({"error": "Order ID is required"}), 400

        # Use PetReservation transition
        reservation_data = {
            "order_id": data["order_id"],
            "transition_name": "PetReservation",
        }

        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=reservation_data,
            entity_class=Pet.ENTITY_NAME,
            transition="PetReservation",
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Reserved Pet %s for order %s", entity_id, data["order_id"])
        return jsonify(_to_entity_dict(response.data)), 200

    except Exception as e:
        logger.exception("Error reserving Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@pet_routes_bp.route("/<entity_id>/release", methods=["PUT"])
async def release_pet(entity_id: str) -> ResponseReturnValue:
    """Release pet reservation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Pet ID is required"}), 400

        data = await request.get_json()
        if not data or not data.get("order_id"):
            return jsonify({"error": "Order ID is required"}), 400

        # Use PetRelease transition
        release_data = {
            "order_id": data["order_id"],
            "reason": data.get("reason", "Order cancelled"),
            "transition_name": "PetRelease",
        }

        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=release_data,
            entity_class=Pet.ENTITY_NAME,
            transition="PetRelease",
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Released Pet %s from order %s", entity_id, data["order_id"])
        return jsonify(_to_entity_dict(response.data)), 200

    except Exception as e:
        logger.exception("Error releasing Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
