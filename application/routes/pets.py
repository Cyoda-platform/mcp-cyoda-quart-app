"""
Pet Routes for Purrfect Pets API

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.pet.version_1.pet import Pet
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


pets_bp = Blueprint("pets", __name__, url_prefix="/pets")


@pets_bp.route("", methods=["GET"])
@tag(["pets"])
@operation_id("get_pets")
async def get_pets() -> ResponseReturnValue:
    """Get all pets with optional filtering"""
    try:
        service = get_entity_service()

        # Get query parameters
        status = request.args.get("status")
        category_id = request.args.get("category_id")
        tags = request.args.get("tags")

        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if status:
            search_conditions["state"] = status
        if category_id:
            search_conditions["category_id"] = category_id
        if tags:
            # Handle comma-separated tags
            tag_list = [tag.strip() for tag in tags.split(",")]
            search_conditions["tags"] = ",".join(tag_list)

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
        pets_data = []
        for entity_response in entities:
            pet_data = _to_entity_dict(entity_response.data)
            pet_data["status"] = entity_response.metadata.state
            pets_data.append(pet_data)

        return jsonify(pets_data), 200

    except Exception as e:
        logger.exception("Error getting pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet")
async def get_pet(pet_id: str) -> ResponseReturnValue:
    """Get pet by ID"""
    try:
        service = get_entity_service()

        response = await service.get_by_id(
            entity_id=pet_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet not found"}), 404

        pet_data = _to_entity_dict(response.data)
        pet_data["status"] = response.metadata.state

        return jsonify(pet_data), 200

    except Exception as e:
        logger.exception("Error getting pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("", methods=["POST"])
@tag(["pets"])
@operation_id("create_pet")
async def create_pet() -> ResponseReturnValue:
    """Add a new pet"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Create Pet entity from request data
        pet = Pet(**data)
        entity_data = pet.model_dump(by_alias=True)

        # Save the entity (will trigger automatic transition to available)
        response = await service.save(
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Created Pet with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "name": pet.name,
                    "status": response.metadata.state,
                    "message": "Pet added successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        logger.warning("Validation error creating pet: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error creating pet: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["PUT"])
@tag(["pets"])
@operation_id("update_pet")
async def update_pet(pet_id: str) -> ResponseReturnValue:
    """Update pet information"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Map transition names to workflow transition names
        transition_map = {
            "reserve": "transition_to_pending",
            "release": "transition_to_available",
            "sell": "transition_to_sold",
            "make_unavailable": "transition_to_unavailable",
            "make_available": "transition_to_available",
            "return": "transition_to_available",
        }

        workflow_transition = None
        if transition:
            workflow_transition = transition_map.get(transition)
            if not workflow_transition:
                return jsonify({"error": f"Invalid transition: {transition}"}), 400

        # Create Pet entity from request data for validation
        pet = Pet(**data)
        entity_data = pet.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=pet_id,
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            transition=workflow_transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", pet_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "name": pet.name,
                    "status": response.metadata.state,
                    "message": f"Pet updated{' and ' + transition if transition else ''} successfully",
                }
            ),
            200,
        )

    except ValueError as e:
        logger.warning("Validation error updating pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error updating pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["DELETE"])
@tag(["pets"])
@operation_id("delete_pet")
async def delete_pet(pet_id: str) -> ResponseReturnValue:
    """Delete pet"""
    try:
        service = get_entity_service()

        await service.delete_by_id(
            entity_id=pet_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", pet_id)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Pet deleted successfully",
                    "entity_id": pet_id,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error deleting pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500
