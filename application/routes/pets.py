"""
Pet Routes for Purrfect Pets API

RESTful API endpoints for pet management operations.
Routes are thin proxies to EntityService with minimal business logic.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service

# Create blueprint for pet routes
pets_bp = Blueprint("pets", __name__, url_prefix="/api/pets")
logger = logging.getLogger(__name__)


@pets_bp.route("", methods=["GET"])
async def get_pets() -> ResponseReturnValue:
    """
    Get all pets with optional filtering.

    Query parameters:
    - state: Filter by pet state (available, reserved, adopted, etc.)
    - category: Filter by pet category
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        entity_service = get_entity_service()

        # Get query parameters
        state = request.args.get("state")
        category = request.args.get("category")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Build filter criteria
        filters = {}
        if state:
            filters["state"] = state
        if category:
            filters["category"] = category

        # Get pets from entity service
        responses = await entity_service.find_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        # Apply filters manually (since find_all doesn't support filters)
        filtered_responses = responses
        if state:
            filtered_responses = [
                r for r in filtered_responses if r.get_state() == state
            ]
        if category:
            filtered_responses = [
                r
                for r in filtered_responses
                if getattr(r.data, "category", None) == category
            ]

        # Apply pagination
        total = len(filtered_responses)
        paginated_responses = filtered_responses[offset : offset + limit]

        # Convert to API response format
        pets = []
        for response in paginated_responses:
            pet = Pet(**response.data.model_dump())
            pets.append(pet.to_api_response())

        return (
            jsonify({"pets": pets, "total": total, "limit": limit, "offset": offset}),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting pets: {str(e)}")
        return jsonify({"error": "Failed to retrieve pets"}), 500


@pets_bp.route("/<pet_id>", methods=["GET"])
async def get_pet(pet_id: str) -> ResponseReturnValue:
    """Get a specific pet by ID."""
    try:
        entity_service = get_entity_service()

        response = await entity_service.get_by_id(
            entity_id=pet_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet not found"}), 404

        pet = Pet(**response.data.model_dump())
        return jsonify(pet.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error getting pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve pet"}), 500


@pets_bp.route("", methods=["POST"])
async def create_pet() -> ResponseReturnValue:
    """Create a new pet."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Create pet entity
        pet = Pet(**data)

        # Save through entity service
        response = await entity_service.save(
            entity=pet.model_dump(by_alias=True),
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        # Return created pet
        created_pet = Pet(**response.data.model_dump())
        return jsonify(created_pet.to_api_response()), 201

    except ValueError as e:
        logger.warning(f"Validation error creating pet: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating pet: {str(e)}")
        return jsonify({"error": "Failed to create pet"}), 500


@pets_bp.route("/<pet_id>", methods=["PUT"])
async def update_pet(pet_id: str) -> ResponseReturnValue:
    """Update an existing pet."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Get transition if provided
        transition = data.pop("transition", None)

        # Update pet through entity service
        response = await entity_service.update(
            entity_id=pet_id,
            entity=data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            transition=transition,
        )

        if not response:
            return jsonify({"error": "Pet not found"}), 404

        # Return updated pet
        updated_pet = Pet(**response.data.model_dump())
        return jsonify(updated_pet.to_api_response()), 200

    except ValueError as e:
        logger.warning(f"Validation error updating pet {pet_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to update pet"}), 500


@pets_bp.route("/<pet_id>", methods=["DELETE"])
async def delete_pet(pet_id: str) -> ResponseReturnValue:
    """Delete a pet."""
    try:
        entity_service = get_entity_service()

        deleted_id = await entity_service.delete_by_id(
            entity_id=pet_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not deleted_id:
            return jsonify({"error": "Pet not found"}), 404

        return jsonify({"message": "Pet deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to delete pet"}), 500


@pets_bp.route("/<pet_id>/reserve", methods=["POST"])
async def reserve_pet(pet_id: str) -> ResponseReturnValue:
    """Reserve a pet for a customer."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data or "customer_id" not in data:
            return jsonify({"error": "customer_id is required"}), 400

        customer_id = data["customer_id"]

        # Execute reservation transition
        response = await entity_service.execute_transition(
            entity_id=pet_id,
            transition="transition_to_reserved",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet not found or cannot be reserved"}), 404

        # Return updated pet
        updated_pet = Pet(**response.data.model_dump())
        return jsonify(updated_pet.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error reserving pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to reserve pet"}), 500


@pets_bp.route("/<pet_id>/adopt", methods=["POST"])
async def adopt_pet(pet_id: str) -> ResponseReturnValue:
    """Finalize pet adoption."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data or "application_id" not in data:
            return jsonify({"error": "application_id is required"}), 400

        application_id = data["application_id"]

        # Execute adoption transition
        response = await entity_service.execute_transition(
            entity_id=pet_id,
            transition="transition_to_adopted",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet not found or cannot be adopted"}), 404

        # Return updated pet
        updated_pet = Pet(**response.data.model_dump())
        return jsonify(updated_pet.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error adopting pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to adopt pet"}), 500


@pets_bp.route("/<pet_id>/medical-hold", methods=["POST"])
async def medical_hold_pet(pet_id: str) -> ResponseReturnValue:
    """Place a pet on medical hold."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        medical_reason = (
            data.get("medical_reason", "Medical attention required")
            if data
            else "Medical attention required"
        )

        # Execute medical hold transition
        response = await entity_service.execute_transition(
            entity_id=pet_id,
            transition="transition_to_medical_hold",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return (
                jsonify({"error": "Pet not found or cannot be placed on medical hold"}),
                404,
            )

        # Return updated pet
        updated_pet = Pet(**response.data.model_dump())
        return jsonify(updated_pet.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error placing pet {pet_id} on medical hold: {str(e)}")
        return jsonify({"error": "Failed to place pet on medical hold"}), 500


@pets_bp.route("/<pet_id>/cancel-reservation", methods=["POST"])
async def cancel_reservation(pet_id: str) -> ResponseReturnValue:
    """Cancel a pet reservation."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        cancellation_reason = (
            data.get("cancellation_reason", "Reservation cancelled")
            if data
            else "Reservation cancelled"
        )

        # Execute cancellation transition (reserved -> available)
        response = await entity_service.execute_transition(
            entity_id=pet_id,
            transition="transition_to_available",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return (
                jsonify({"error": "Pet not found or reservation cannot be cancelled"}),
                404,
            )

        # Return updated pet
        updated_pet = Pet(**response.data.model_dump())
        return jsonify(updated_pet.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error cancelling reservation for pet {pet_id}: {str(e)}")
        return jsonify({"error": "Failed to cancel reservation"}), 500
