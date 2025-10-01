"""
Pet Routes for Cyoda Petstore Application

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions following OpenAPI Petstore specification.
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

# Imported for entity constants / typing
from ..entity.pet.version_1.pet import Pet
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    PetListResponse,
    PetQueryParams,
    PetResponse,
    PetSearchResponse,
    PetUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

# Module-level service instance to avoid repeated lookups
# Lazy proxy to avoid initializing services at import time


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


logger = logging.getLogger(__name__)


# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


pets_bp = Blueprint("pets", __name__, url_prefix="/api/pets")


# ---- Routes -----------------------------------------------------------------


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
    """Create a new Pet with comprehensive validation"""
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

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Pet: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:  # pragma: no cover
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
    """Get Pet by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error getting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


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
    """List Pets with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["status"] = query_args.status

        if query_args.breed:
            search_conditions["breed"] = query_args.breed

        if query_args.category:
            search_conditions["category.name"] = query_args.category

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

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply price filtering if specified
        if query_args.min_price is not None or query_args.max_price is not None:
            filtered_list = []
            for entity in entity_list:
                price = entity.get("price")
                if price is not None:
                    if query_args.min_price is not None and price < query_args.min_price:
                        continue
                    if query_args.max_price is not None and price > query_args.max_price:
                        continue
                filtered_list.append(entity)
            entity_list = filtered_list

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"pets": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing Pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


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
    """Update Pet and optionally trigger workflow transition with validation"""
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
            entity_class=Pet.ENTITY_NAME,
            transition=transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:  # pragma: no cover
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
    """Delete Pet with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Pet deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@pets_bp.route("/by-business-id/<business_id>", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet_by_business_id")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get Pet by business ID (name field by default)"""
    try:
        business_id_field = request.args.get("field", "name")  # Default to name field

        result = await service.find_by_business_id(
            entity_class=Pet.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "Pet not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception("Error getting Pet by business ID %s: %s", business_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["pets"])
@operation_id("check_pet_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Pet exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Pet existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/count", methods=["GET"])
@tag(["pets"])
@operation_id("count_pets")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Pets"""
    try:
        service = get_entity_service()

        count = await service.count(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


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
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Pet"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error getting transitions for Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@pets_bp.route("/search", methods=["POST"])
@tag(["pets"])
@operation_id("search_pets")
@validate(
    request=SearchRequest,
    responses={
        200: (PetSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Pets using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # KISS: Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            if field in ["min_price", "max_price"]:
                continue  # Handle price range separately
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        # Apply price range filtering if specified
        if data.min_price is not None or data.max_price is not None:
            filtered_entities = []
            for entity in entities:
                price = entity.get("price")
                if price is not None:
                    if data.min_price is not None and price < data.min_price:
                        continue
                    if data.max_price is not None and price > data.max_price:
                        continue
                filtered_entities.append(entity)
            entities = filtered_entities

        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Pets: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/find-all", methods=["GET"])
@tag(["pets"])
@operation_id("find_all_pets")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def find_all_entities() -> ResponseReturnValue:
    """Find all Pets without filtering"""
    try:
        results = await service.find_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding all Pets: %s", str(e))
        return {"error": str(e)}, 500


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
async def trigger_transition(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Trigger a specific workflow transition with validation"""
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

        logger.info("Executed transition '%s' on Pet %s", data.transition_name, entity_id)

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

    except Exception as e:  # pragma: no cover
        logger.exception("Error executing transition on Pet %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


# ---- Petstore-specific endpoints ------------------------------------------------


@pets_bp.route("/findByStatus", methods=["GET"])
@tag(["pets"])
@operation_id("find_pets_by_status")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def find_by_status() -> ResponseReturnValue:
    """Find Pets by status (OpenAPI Petstore compatibility)"""
    try:
        status = request.args.get("status", "available")

        # Build search condition
        builder = SearchConditionRequest.builder()
        builder.equals("status", status)
        condition = builder.build()

        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=condition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding Pets by status: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/findByTags", methods=["GET"])
@tag(["pets"])
@operation_id("find_pets_by_tags")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def find_by_tags() -> ResponseReturnValue:
    """Find Pets by tags (OpenAPI Petstore compatibility)"""
    try:
        tags = request.args.getlist("tags")

        if not tags:
            return {"pets": [], "total": 0}, 200

        # For simplicity, find all pets and filter by tags in memory
        results = await service.find_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]

        # Filter by tags
        filtered_entities = []
        for entity in entities:
            entity_tags = entity.get("tags", [])
            if entity_tags:
                tag_names = [tag.get("name", "") for tag in entity_tags if isinstance(tag, dict)]
                if any(tag in tag_names for tag in tags):
                    filtered_entities.append(entity)

        return {"pets": filtered_entities, "total": len(filtered_entities)}, 200

    except Exception as e:
        logger.exception("Error finding Pets by tags: %s", str(e))
        return {"error": str(e)}, 500
