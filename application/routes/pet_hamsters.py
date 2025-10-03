"""
PetHamster Routes for Cyoda Client Application

Manages all PetHamster-related API endpoints including CRUD operations
and workflow transitions for the pet hamster workflow.
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
from ..entity.pet_hamster.version_1.pet_hamster import PetHamster  # noqa: F401
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    PetHamsterListResponse,
    PetHamsterQueryParams,
    PetHamsterResponse,
    PetHamsterSearchResponse,
    PetHamsterUpdateQueryParams,
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


pet_hamsters_bp = Blueprint("pet_hamsters", __name__, url_prefix="/api/pet-hamsters")


# ---- Routes -----------------------------------------------------------------


@pet_hamsters_bp.route("", methods=["POST"])
@tag(["pet-hamsters"])
@operation_id("create_pet_hamster")
@validate(
    request=PetHamster,
    responses={
        201: (PetHamsterResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_pet_hamster(
    data: PetHamster,
) -> ResponseReturnValue:
    """Create a new PetHamster with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        logger.info("Created PetHamster with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating PetHamster: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:  # pragma: no cover - keep robust error handling
        logger.exception("Error creating PetHamster: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@pet_hamsters_bp.route("/<entity_id>", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("get_pet_hamster")
@validate(
    responses={
        200: (PetHamsterResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_pet_hamster(entity_id: str) -> ResponseReturnValue:
    """Get PetHamster by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        if not response:
            return {"error": "PetHamster not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error getting PetHamster %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@pet_hamsters_bp.route("", methods=["GET"])
@validate_querystring(PetHamsterQueryParams)
@tag(["pet-hamsters"])
@operation_id("list_pet_hamsters")
@validate(
    responses={
        200: (PetHamsterListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_pet_hamsters(
    query_args: PetHamsterQueryParams,
) -> ResponseReturnValue:
    """List PetHamsters with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.mood:
            search_conditions["mood"] = query_args.mood

        if query_args.is_safe_to_handle is not None:
            search_conditions["isSafeToHandle"] = str(
                query_args.is_safe_to_handle
            ).lower()

        if query_args.current_location:
            search_conditions["currentLocation"] = query_args.current_location

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
                entity_class=PetHamster.ENTITY_NAME,
                condition=condition,
                entity_version=str(PetHamster.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=PetHamster.ENTITY_NAME,
                entity_version=str(PetHamster.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing PetHamsters: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pet_hamsters_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PetHamsterUpdateQueryParams)
@tag(["pet-hamsters"])
@operation_id("update_pet_hamster")
@validate(
    request=PetHamster,
    responses={
        200: (PetHamsterResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_pet_hamster(
    entity_id: str, data: PetHamster, query_args: PetHamsterUpdateQueryParams
) -> ResponseReturnValue:
    """Update PetHamster and optionally trigger workflow transition with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data (entity model as-is)
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=PetHamster.ENTITY_NAME,
            transition=transition,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        logger.info("Updated PetHamster %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating PetHamster %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error updating PetHamster %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@pet_hamsters_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["pet-hamsters"])
@operation_id("delete_pet_hamster")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_pet_hamster(entity_id: str) -> ResponseReturnValue:
    """Delete PetHamster with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        logger.info("Deleted PetHamster %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="PetHamster deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error deleting PetHamster %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@pet_hamsters_bp.route("/by-business-id/<business_id>", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("get_pet_hamster_by_business_id")
@validate(
    responses={
        200: (PetHamsterResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get PetHamster by business ID (name field by default)"""
    try:
        business_id_field = request.args.get("field", "name")  # Default to name field

        result = await service.find_by_business_id(
            entity_class=PetHamster.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "PetHamster not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception(
            "Error getting PetHamster by business ID %s: %s", business_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@pet_hamsters_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("check_pet_hamster_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if PetHamster exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking PetHamster existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@pet_hamsters_bp.route("/count", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("count_pet_hamsters")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of PetHamsters"""
    try:
        service = get_entity_service()

        count = await service.count(
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting PetHamsters: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pet_hamsters_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("get_pet_hamster_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for PetHamster"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for PetHamster %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@pet_hamsters_bp.route("/search", methods=["POST"])
@tag(["pet-hamsters"])
@operation_id("search_pet_hamsters")
@validate(
    request=SearchRequest,
    responses={
        200: (PetHamsterSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search PetHamsters using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # KISS: Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=PetHamster.ENTITY_NAME,
            condition=search_request,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching PetHamsters: %s", str(e))
        return {"error": str(e)}, 500


@pet_hamsters_bp.route("/find-all", methods=["GET"])
@tag(["pet-hamsters"])
@operation_id("find_all_pet_hamsters")
@validate(responses={200: (PetHamsterListResponse, None), 500: (ErrorResponse, None)})
async def find_all_entities() -> ResponseReturnValue:
    """Find all PetHamsters without filtering"""
    try:
        results = await service.find_all(
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding all PetHamsters: %s", str(e))
        return {"error": str(e)}, 500


@pet_hamsters_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["pet-hamsters"])
@operation_id("trigger_pet_hamster_transition")
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
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "PetHamster not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=PetHamster.ENTITY_NAME,
            entity_version=str(PetHamster.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on PetHamster %s",
            data.transition_name,
            entity_id,
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

    except Exception as e:  # pragma: no cover
        logger.exception(
            "Error executing transition on PetHamster %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
