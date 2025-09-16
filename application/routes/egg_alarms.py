"""
EggAlarm Routes for Cyoda Client Application

Manages all EggAlarm-related API endpoints including CRUD operations
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

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

# Imported for entity constants / typing
from ..entity.eggalarm.version_1.eggalarm import EggAlarm
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
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


egg_alarms_bp = Blueprint("egg_alarms", __name__, url_prefix="/api/egg-alarms")

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
async def create_egg_alarm(data: EggAlarm) -> ResponseReturnValue:
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
    except Exception as e:
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
    except Exception as e:
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
async def list_egg_alarms(query_args: EggAlarmQueryParams) -> ResponseReturnValue:
    """List EggAlarms with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.userId:
            search_conditions["userId"] = query_args.userId

        if query_args.eggType:
            search_conditions["eggType"] = query_args.eggType

        if query_args.isActive is not None:
            search_conditions["isActive"] = str(query_args.isActive).lower()

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

        return jsonify({"alarms": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
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

        # Convert request to entity data
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
        logger.warning("Validation error updating EggAlarm %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
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
            success=True, message="EggAlarm deleted successfully", entity_id=entity_id
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Workflow Action Endpoints ----------------------------------------


@egg_alarms_bp.route("/<entity_id>/start", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("start_egg_alarm")
@validate(
    request=TransitionRequest,
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def start_egg_alarm(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Start/activate an egg alarm"""
    try:
        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Started EggAlarm %s", entity_id)

        # Return updated entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error starting EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@egg_alarms_bp.route("/<entity_id>/cancel", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("cancel_egg_alarm")
@validate(
    request=TransitionRequest,
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def cancel_egg_alarm(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Cancel an egg alarm"""
    try:
        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Cancelled EggAlarm %s", entity_id)

        # Return updated entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error cancelling EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@egg_alarms_bp.route("/<entity_id>/reset", methods=["POST"])
@tag(["egg-alarms"])
@operation_id("reset_egg_alarm")
@validate(
    request=TransitionRequest,
    responses={
        200: (EggAlarmResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def reset_egg_alarm(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Reset a completed alarm to create a new one"""
    try:
        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=EggAlarm.ENTITY_NAME,
            entity_version=str(EggAlarm.ENTITY_VERSION),
        )

        logger.info("Reset EggAlarm %s", entity_id)

        # Return new entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error resetting EggAlarm %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
