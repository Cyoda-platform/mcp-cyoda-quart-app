"""
Pet Routes for Cyoda Pet Search Application

Manages all Pet-related API endpoints including search functionality
with filtering by species, status, and category ID as specified in functional requirements.
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

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

# Import Pet entity and models
from ..entity.pet.version_1.pet import Pet
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    PetListResponse,
    PetQueryParams,
    PetResponse,
    PetSearchRequest,
    PetSearchResponse,
    PetUpdateQueryParams,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


pets_bp = Blueprint("pets", __name__, url_prefix="/api/pets")


# ---- Core CRUD Operations ----


@pets_bp.route("", methods=["POST"])
@tag(["pets"])
@operation_id("create_pet")
@validate(
    request=Pet,
    responses={
        201: (PetResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_pet(data: Pet) -> ResponseReturnValue:
    """Create a new Pet for search and processing"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Created Pet with ID: %s", response.metadata.id)

        # Return created entity
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Pet: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Pet: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@pets_bp.route("/<entity_id>", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_pet(entity_id: str) -> ResponseReturnValue:
    """Get Pet by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Pet Search Endpoints ----


@pets_bp.route("", methods=["GET"])
@validate_querystring(PetQueryParams)
@tag(["pets"])
@operation_id("list_pets")
@validate(
    responses={
        200: (PetListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_pets(query_args: PetQueryParams) -> ResponseReturnValue:
    """List Pets with filtering by species, status, and category ID"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.species:
            search_conditions["species"] = query_args.species

        if query_args.status:
            search_conditions["status"] = query_args.status

        if query_args.category_id is not None:
            # Search in category.id field
            search_conditions["category.id"] = str(query_args.category_id)

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
                entity_class=Pet.ENTITY_NAME,
                condition=condition,
                entity_version=str(Pet.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

        # Convert to list and apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]

        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"pets": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/search", methods=["POST"])
@tag(["pets"])
@operation_id("search_pets")
@validate(
    request=PetSearchRequest,
    responses={
        200: (PetSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_pets(data: PetSearchRequest) -> ResponseReturnValue:
    """Search Pets using multiple criteria for the Pet Search Application"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Build search conditions
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            if field == "categoryId":
                # Handle category ID search
                builder.equals("category.id", str(value))
            else:
                builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        # Convert results
        pets = [_to_entity_dict(r.data) for r in results]

        return {"pets": pets, "total": len(pets), "searchCriteria": search_data}, 200

    except Exception as e:
        logger.exception("Error searching Pets: %s", str(e))
        return {"error": str(e)}, 500


# ---- Pet Search with External API Integration ----


@pets_bp.route("/search-external", methods=["POST"])
@tag(["pets"])
@operation_id("search_pets_external")
@validate(
    request=PetSearchRequest,
    responses={
        200: (PetSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_pets_external(data: PetSearchRequest) -> ResponseReturnValue:
    """Search Pets with external API integration - creates new Pet entities with search criteria"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Create a new Pet entity with search parameters for processing
        pet_data = {
            "name": f"Search Result for {search_data.get('species', 'Pet')}",
            "searchSpecies": search_data.get("species"),
            "searchStatus": search_data.get("status", "available"),
            "searchCategoryId": search_data.get("categoryId"),
            "status": "available",
            "photoUrls": [],  # Will be populated by ingestion processor
        }

        # Save the pet entity - this will trigger the workflow
        response = await service.save(
            entity=pet_data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        created_pet = _to_entity_dict(response.data)

        logger.info("Created Pet for external search with ID: %s", response.metadata.id)

        return {
            "pets": [created_pet],
            "total": 1,
            "searchCriteria": search_data,
            "message": "Pet created and will be processed through ingestion and transformation workflow",
        }, 200

    except Exception as e:
        logger.exception("Error in external pet search: %s", str(e))
        return {"error": str(e)}, 500


# ---- Update and Delete Operations ----


@pets_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PetUpdateQueryParams)
@tag(["pets"])
@operation_id("update_pet")
@validate(
    request=Pet,
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_pet(
    entity_id: str, data: Pet, query_args: PetUpdateQueryParams
) -> ResponseReturnValue:
    """Update Pet and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            transition=transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@pets_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["pets"])
@operation_id("delete_pet")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_pet(entity_id: str) -> ResponseReturnValue:
    """Delete Pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="Pet deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Service Endpoints ----


@pets_bp.route("/count", methods=["GET"])
@tag(["pets"])
@operation_id("count_pets")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_pets() -> ResponseReturnValue:
    """Count total number of Pets"""
    try:
        count = await service.count(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["pets"])
@operation_id("check_pet_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_pet_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Pet exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entityId=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Pet existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_pet_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Pet"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entityId=entity_id,
            availableTransitions=transitions,
            currentState=None,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error getting transitions for Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["pets"])
@operation_id("trigger_pet_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_pet_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Pet not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Pet %s", data.transition_name, entity_id
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
        logger.exception("Error executing transition on Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


# ---- Pet Search Application Specific Endpoints ----


@pets_bp.route("/find-all", methods=["GET"])
@tag(["pets"])
@operation_id("find_all_pets")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def find_all_pets() -> ResponseReturnValue:
    """Find all Pets without filtering"""
    try:
        results = await service.find_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        pets = [_to_entity_dict(r.data) for r in results]
        return {"pets": pets, "total": len(pets)}, 200

    except Exception as e:
        logger.exception("Error finding all Pets: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/available", methods=["GET"])
@tag(["pets"])
@operation_id("get_available_pets")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def get_available_pets() -> ResponseReturnValue:
    """Get all available pets for adoption"""
    try:
        builder = SearchConditionRequest.builder()
        builder.equals("status", "available")
        condition = builder.build()

        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=condition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        pets = [_to_entity_dict(r.data) for r in results]
        return {"pets": pets, "total": len(pets)}, 200

    except Exception as e:
        logger.exception("Error getting available pets: %s", str(e))
        return {"error": str(e)}, 500
