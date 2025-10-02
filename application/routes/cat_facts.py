"""
Cat Fact Routes for Cat Fact Subscription Application

Manages all CatFact-related API endpoints including CRUD operations
and workflow transitions.
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

from ..entity.cat_fact.version_1.cat_fact import CatFact
from ..models import (
    CatFactListResponse,
    CatFactQueryParams,
    CatFactResponse,
    CatFactSearchResponse,
    CatFactUpdateQueryParams,
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

# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

cat_facts_bp = Blueprint(
    "cat_facts", __name__, url_prefix="/api/cat-facts"
)


@cat_facts_bp.route("", methods=["POST"])
@tag(["cat-facts"])
@operation_id("create_cat_fact")
@validate(
    request=CatFact,
    responses={
        201: (CatFactResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_cat_fact(data: CatFact) -> ResponseReturnValue:
    """Create a new CatFact"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Created CatFact with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/<entity_id>", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_cat_fact")
@validate(
    responses={
        200: (CatFactResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Get CatFact by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        if not response:
            return {"error": "CatFact not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("", methods=["GET"])
@validate_querystring(CatFactQueryParams)
@tag(["cat-facts"])
@operation_id("list_cat_facts")
@validate(
    responses={
        200: (CatFactListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_cat_facts(query_args: CatFactQueryParams) -> ResponseReturnValue:
    """List CatFacts with optional filtering"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.is_used_for_delivery is not None:
            search_conditions["isUsedForDelivery"] = str(query_args.is_used_for_delivery).lower()

        if query_args.is_appropriate is not None:
            search_conditions["isAppropriate"] = str(query_args.is_appropriate).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.source_api:
            search_conditions["sourceApi"] = query_args.source_api

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=CatFact.ENTITY_NAME,
                condition=condition,
                entity_version=str(CatFact.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=CatFact.ENTITY_NAME,
                entity_version=str(CatFact.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(CatFactUpdateQueryParams)
@tag(["cat-facts"])
@operation_id("update_cat_fact")
@validate(
    request=CatFact,
    responses={
        200: (CatFactResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_cat_fact(
    entity_id: str, data: CatFact, query_args: CatFactUpdateQueryParams
) -> ResponseReturnValue:
    """Update CatFact and optionally trigger workflow transition"""
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
            entity_class=CatFact.ENTITY_NAME,
            transition=transition,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Updated CatFact %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating CatFact %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@cat_facts_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["cat-facts"])
@operation_id("delete_cat_fact")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Delete CatFact"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Deleted CatFact %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="CatFact deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/ready-for-delivery", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_ready_cat_facts")
@validate(
    responses={
        200: (CatFactListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_ready_for_delivery() -> ResponseReturnValue:
    """Get CatFacts that are ready for delivery"""
    try:
        # Search for facts ready for delivery
        builder = SearchConditionRequest.builder()
        builder.equals("state", "ready_for_delivery")
        builder.equals("isAppropriate", "true")
        builder.equals("isUsedForDelivery", "false")
        condition = builder.build()

        entities = await service.search(
            entity_class=CatFact.ENTITY_NAME,
            condition=condition,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        # Return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]
        return jsonify({"entities": entity_list, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error getting ready CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["cat-facts"])
@operation_id("check_cat_fact_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if CatFact exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking CatFact existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@cat_facts_bp.route("/count", methods=["GET"])
@tag(["cat-facts"])
@operation_id("count_cat_facts")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of CatFacts"""
    try:
        count = await service.count(
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_cat_fact_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for CatFact"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for CatFact %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@cat_facts_bp.route("/search", methods=["POST"])
@tag(["cat-facts"])
@operation_id("search_cat_facts")
@validate(
    request=SearchRequest,
    responses={
        200: (CatFactSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search CatFacts using simple field-value search"""
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
            entity_class=CatFact.ENTITY_NAME,
            condition=search_request,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching CatFacts: %s", str(e))
        return {"error": str(e)}, 500


@cat_facts_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["cat-facts"])
@operation_id("trigger_cat_fact_transition")
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
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "CatFact not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on CatFact %s",
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

    except Exception as e:
        logger.exception(
            "Error executing transition on CatFact %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
