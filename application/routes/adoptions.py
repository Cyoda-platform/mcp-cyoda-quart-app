"""
Adoption Routes for Purrfect Pets Application

Manages all Adoption-related API endpoints including CRUD operations
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

from application.entity.adoption.version_1.adoption import Adoption
from application.models import (
    AdoptionListResponse,
    AdoptionQueryParams,
    AdoptionResponse,
    AdoptionSearchResponse,
    AdoptionUpdateQueryParams,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    """Helper to normalize entity data from service."""
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


adoptions_bp = Blueprint("adoptions", __name__, url_prefix="/api/adoptions")


@adoptions_bp.route("", methods=["POST"])
@tag(["adoptions"])
@operation_id("create_adoption")
@validate(
    request=Adoption,
    responses={
        201: (AdoptionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_adoption(data: Adoption) -> ResponseReturnValue:
    """Create a new adoption with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        logger.info("Created Adoption with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Adoption: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Adoption: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@adoptions_bp.route("/<entity_id>", methods=["GET"])
@tag(["adoptions"])
@operation_id("get_adoption")
@validate(
    responses={
        200: (AdoptionResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_adoption(entity_id: str) -> ResponseReturnValue:
    """Get Adoption by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Adoption not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@adoptions_bp.route("", methods=["GET"])
@validate_querystring(AdoptionQueryParams)
@tag(["adoptions"])
@operation_id("list_adoptions")
@validate(
    responses={
        200: (AdoptionListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_adoptions(query_args: AdoptionQueryParams) -> ResponseReturnValue:
    """List Adoptions with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.pet_id:
            search_conditions["pet_id"] = query_args.pet_id

        if query_args.owner_id:
            search_conditions["owner_id"] = query_args.owner_id

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
                entity_class=Adoption.ENTITY_NAME,
                condition=condition,
                entity_version=str(Adoption.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Adoption.ENTITY_NAME,
                entity_version=str(Adoption.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return (
            jsonify({"adoptions": paginated_entities, "total": len(entity_list)}),
            200,
        )

    except Exception as e:
        logger.exception("Error listing Adoptions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@adoptions_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(AdoptionUpdateQueryParams)
@tag(["adoptions"])
@operation_id("update_adoption")
@validate(
    request=Adoption,
    responses={
        200: (AdoptionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_adoption(
    entity_id: str, data: Adoption, query_args: AdoptionUpdateQueryParams
) -> ResponseReturnValue:
    """Update Adoption and optionally trigger workflow transition with validation"""
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
            entity_class=Adoption.ENTITY_NAME,
            transition=transition,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        logger.info("Updated Adoption %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Adoption %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Adoption %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@adoptions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["adoptions"])
@operation_id("delete_adoption")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_adoption(entity_id: str) -> ResponseReturnValue:
    """Delete Adoption with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        logger.info("Deleted Adoption %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Adoption deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@adoptions_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["adoptions"])
@operation_id("check_adoption_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Adoption exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Adoption existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@adoptions_bp.route("/count", methods=["GET"])
@tag(["adoptions"])
@operation_id("count_adoptions")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Adoptions"""
    try:
        count = await service.count(
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Adoptions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@adoptions_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["adoptions"])
@operation_id("get_adoption_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Adoption"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for Adoption %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@adoptions_bp.route("/search", methods=["POST"])
@tag(["adoptions"])
@operation_id("search_adoptions")
@validate(
    request=SearchRequest,
    responses={
        200: (AdoptionSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Adoptions using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Adoption.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"adoptions": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Adoptions: %s", str(e))
        return {"error": str(e)}, 500


@adoptions_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["adoptions"])
@operation_id("trigger_adoption_transition")
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
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Adoption not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Adoption %s", data.transition_name, entity_id
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
        logger.exception(
            "Error executing transition on Adoption %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
