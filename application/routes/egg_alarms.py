"""
EggAlarm Routes for Cyoda Client Application

Manages all EggAlarm-related API endpoints including CRUD operations
and workflow transitions for the egg cooking alarm functionality.
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
from ..entity.egg_alarm.version_1.egg_alarm import EggAlarm  # noqa: F401
from ..models import (
    CountResponse,
    DeleteResponse,
    EggAlarmListResponse,
    EggAlarmQueryParams,
    EggAlarmResponse,
    EggAlarmSearchResponse,
    EggAlarmUpdateQueryParams,
    ErrorResponse,
    ExistsResponse,
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


egg_alarms_bp = Blueprint(
    "egg_alarms", __name__, url_prefix="/api/egg-alarms"
)


# ---- Routes -----------------------------------------------------------------


@egg_alarms_bp.route("", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("create_egg_alarm")
@validate(
    request=EggAlarm,
    responses={
        201: (EggAlarmResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_egg_alarm(
    data: EggAlarm,
) -> ResponseReturnValue:
    """Create a new EggAlarm with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Created EggAlarm with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating EggAlarm: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:  # pragma: no cover - keep robust error handling
        logger.exception("Error creating EggAlarm: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@egg_alarms_bp.route("/<entity_id>", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("get_egg_alarm")
@validate(
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_egg_alarm(entity_id: str) -> ResponseReturnValue:
    """Get EggAlarm by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        if not response:
            return {"error": "EggAlarm not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error getting EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@egg_alarms_bp.route("", methods=["GET"])
@validate_querystring(EggAlarmQueryParams)
@tag(["egg-alarms"])
@operation_id("list_egg_alarms")
@validate(
    responses={
        200: (EggAlarmListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_egg_alarms(
    query_args: EggAlarmQueryParams,
) -> ResponseReturnValue:
    """List EggAlarms with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.egg_type:
            search_conditions["eggType"] = query_args.egg_type.value

        if query_args.status:
            search_conditions["status"] = query_args.status.value

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.created_by:
            search_conditions["createdBy"] = query_args.created_by

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=EggAlarm.ENTITY_NAME,
                condition=condition,
                entity_version=str(EggAlarm.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=EggAlarm.ENTITY_NAME,
                entity_version=str(EggAlarm.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing EggAlarms: %s", str(e))
        return jsonify({"error": str(e)}), 500


@egg_alarms_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(EggAlarmUpdateQueryParams)
@tag(["egg-alarms"])
@operation_id("update_egg_alarm")
@validate(
    request=EggAlarm,
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_egg_alarm(
    entity_id: str, data: EggAlarm, query_args: EggAlarmUpdateQueryParams
) -> ResponseReturnValue:
    """Update EggAlarm and optionally trigger workflow transition with validation"""
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
            entity_class=EggAlarm.ENTITY_NAME,
            transition=transition,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Updated EggAlarm %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating EggAlarm %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error updating EggAlarm %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@egg_alarms_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["egg-alarms"])
@operation_id("delete_egg_alarm")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_egg_alarm(entity_id: str) -> ResponseReturnValue:
    """Delete EggAlarm with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Deleted EggAlarm %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="EggAlarm deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error deleting EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@egg_alarms_bp.route("/by-business-id/<business_id>", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("get_egg_alarm_by_business_id")
@validate(
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get EggAlarm by business ID (created_by field by default)"""
    try:
        business_id_field = request.args.get("field", "createdBy")  # Default to createdBy field

        result = await service.find_by_business_id(
            entity_class=EggAlarm.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "EggAlarm not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception(
            "Error getting EggAlarm by business ID %s: %s", business_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@egg_alarms_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("check_egg_alarm_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if EggAlarm exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking EggAlarm existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@egg_alarms_bp.route("/count", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("count_egg_alarms")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of EggAlarms"""
    try:
        service = get_entity_service()

        count = await service.count(
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting EggAlarms: %s", str(e))
        return jsonify({"error": str(e)}), 500


@egg_alarms_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("get_egg_alarm_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for EggAlarm"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for EggAlarm %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@egg_alarms_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("trigger_egg_alarm_transition")
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
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "EggAlarm not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on EggAlarm %s",
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
            "Error executing transition on EggAlarm %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@egg_alarms_bp.route("/search", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("search_egg_alarms")
@validate(
    request=SearchRequest,
    responses={
        200: (EggAlarmSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search EggAlarms using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # KISS: Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            if field == "eggType" and hasattr(value, "value"):
                builder.equals(field, value.value)
            elif field == "status" and hasattr(value, "value"):
                builder.equals(field, value.value)
            else:
                builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=EggAlarm.ENTITY_NAME,
            condition=search_request,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching EggAlarms: %s", str(e))
        return {"error": str(e)}, 500


@egg_alarms_bp.route("/find-all", methods=["GET"])
@tag(["egg-alarms"])
@operation_id("find_all_egg_alarms")
@validate(
    responses={200: (EggAlarmListResponse, None), 500: (ErrorResponse, None)}
)
async def find_all_entities() -> ResponseReturnValue:
    """Find all EggAlarms without filtering"""
    try:
        results = await service.find_all(
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding all EggAlarms: %s", str(e))
        return {"error": str(e)}, 500
