"""
Pet Routes for Purrfect Pets API

Manages all Pet-related API endpoints including CRUD operations,
workflow transitions, and adoption-specific functionality.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from decimal import Decimal

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
from ..models.pet_models import (
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

# ---- CRUD Routes ----


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
    """Create a new pet in the system"""
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
    """Get pet by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Pet ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid pet ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
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
    """List pets with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.species:
            search_conditions["species"] = query_args.species
        if query_args.breed:
            search_conditions["breed"] = query_args.breed
        if query_args.size:
            search_conditions["size"] = query_args.size
        if query_args.gender:
            search_conditions["gender"] = query_args.gender
        if query_args.adoption_status:
            search_conditions["adoptionStatus"] = query_args.adoption_status
        if query_args.health_status:
            search_conditions["healthStatus"] = query_args.health_status
        if query_args.state:
            search_conditions["state"] = query_args.state

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

        # Convert to list and apply additional filters
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply age and price filters (client-side filtering)
        filtered_entities = []
        for entity in entity_list:
            age_months = entity.get("ageMonths", 0)
            price = Decimal(str(entity.get("price", 0)))

            # Age filters
            if query_args.min_age is not None and age_months < query_args.min_age:
                continue
            if query_args.max_age is not None and age_months > query_args.max_age:
                continue

            # Price filters
            if query_args.min_price is not None and price < query_args.min_price:
                continue
            if query_args.max_price is not None and price > query_args.max_price:
                continue

            filtered_entities.append(entity)

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = filtered_entities[start:end]

        return {"pets": paginated_entities, "total": len(filtered_entities)}, 200

    except Exception as e:
        logger.exception("Error listing Pets: %s", str(e))
        return {"error": str(e)}, 500


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
    """Update pet and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Pet ID is required", "code": "INVALID_ID"}, 400

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
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


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
    """Delete pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Pet ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="Pet deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid pet ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Service Endpoints ----


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
    """Get pet by business ID (name field by default)"""
    try:
        business_id_field = request.args.get("field", "name")

        result = await service.find_by_business_id(
            entity_class=Pet.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not result:
            return {"error": "Pet not found"}, 404

        return _to_entity_dict(result.data), 200

    except Exception as e:
        logger.exception("Error getting Pet by business ID %s: %s", business_id, str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["pets"])
@operation_id("check_pet_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if pet exists by ID"""
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
    """Count total number of pets"""
    try:
        count = await service.count(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting Pets: %s", str(e))
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
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for pet"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,
        )
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error getting transitions for Pet %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


# ---- Search Endpoints ----


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
async def search_entities(data: PetSearchRequest) -> ResponseReturnValue:
    """Search pets using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Pets: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/find-all", methods=["GET"])
@tag(["pets"])
@operation_id("find_all_pets")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def find_all_entities() -> ResponseReturnValue:
    """Find all pets without filtering"""
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
async def trigger_transition(
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
            return {"error": "Pet not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Pet %s",
            data.transition_name,
            entity_id,
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error executing transition on Pet %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


# ---- Pet-specific Endpoints ----


@pets_bp.route("/available", methods=["GET"])
@tag(["pets"])
@operation_id("get_available_pets")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def get_available_pets() -> ResponseReturnValue:
    """Get all pets available for adoption"""
    try:
        builder = SearchConditionRequest.builder()
        builder.equals("adoptionStatus", "Available")
        condition = builder.build()

        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=condition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error getting available pets: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/species/<species>", methods=["GET"])
@tag(["pets"])
@operation_id("get_pets_by_species")
@validate(responses={200: (PetListResponse, None), 500: (ErrorResponse, None)})
async def get_pets_by_species(species: str) -> ResponseReturnValue:
    """Get all pets of a specific species"""
    try:
        builder = SearchConditionRequest.builder()
        builder.equals("species", species)
        condition = builder.build()

        results = await service.search(
            entity_class=Pet.ENTITY_NAME,
            condition=condition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"pets": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error getting pets by species %s: %s", species, str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/statistics", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet_statistics")
@validate(responses={200: (Dict, None), 500: (ErrorResponse, None)})
async def get_pet_statistics() -> ResponseReturnValue:
    """Get pet statistics and analytics"""
    try:
        # Get all pets
        results = await service.find_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]

        # Calculate statistics
        total_pets = len(entities)
        available_pets = sum(
            1 for e in entities if e.get("adoptionStatus") == "Available"
        )
        reserved_pets = sum(
            1 for e in entities if e.get("adoptionStatus") == "Reserved"
        )
        adopted_pets = sum(1 for e in entities if e.get("adoptionStatus") == "Adopted")

        # Count by species
        by_species = {}
        by_size = {}
        by_health_status = {}
        total_age = 0
        total_price = 0

        for entity in entities:
            species = entity.get("species", "Unknown")
            by_species[species] = by_species.get(species, 0) + 1

            size = entity.get("size", "Unknown")
            by_size[size] = by_size.get(size, 0) + 1

            health = entity.get("healthStatus", "Unknown")
            by_health_status[health] = by_health_status.get(health, 0) + 1

            total_age += entity.get("ageMonths", 0)
            total_price += float(entity.get("price", 0))

        avg_age = total_age / total_pets if total_pets > 0 else 0
        avg_price = total_price / total_pets if total_pets > 0 else 0

        statistics = {
            "totalPets": total_pets,
            "availablePets": available_pets,
            "reservedPets": reserved_pets,
            "adoptedPets": adopted_pets,
            "bySpecies": by_species,
            "bySize": by_size,
            "byHealthStatus": by_health_status,
            "averageAgeMonths": round(avg_age, 1),
            "averagePrice": round(avg_price, 2),
        }

        return statistics, 200

    except Exception as e:
        logger.exception("Error getting pet statistics: %s", str(e))
        return {"error": str(e)}, 500
