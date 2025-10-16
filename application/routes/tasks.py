"""
Task Routes for Cyoda Client Application

Manages all Task-related API endpoints including CRUD operations
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

from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service

# Imported for entity constants / typing
from ..entity.task.version_1.task import Task
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    TaskListResponse,
    TaskQueryParams,
    TaskResponse,
    TaskSearchResponse,
    TaskUpdateQueryParams,
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


tasks_bp = Blueprint(
    "tasks", __name__, url_prefix="/api/tasks"
)


# ---- Routes -----------------------------------------------------------------


@tasks_bp.route("", methods=["POST"])
@tag(["tasks"])
@operation_id("create_task")
@validate(
    request=Task,
    responses={
        201: (TaskResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_task(
    data: Task,
) -> ResponseReturnValue:
    """Create a new Task with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Task.ENTITY_NAME,
            entity_version=str(Task.ENTITY_VERSION),
        )

        logger.info("Created Task with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Task: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:  # pragma: no cover - keep robust error handling
        logger.exception("Error creating Task: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@tasks_bp.route("/<entity_id>", methods=["GET"])
@tag(["tasks"])
@operation_id("get_task")
@validate(
    responses={
        200: (TaskResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_task(entity_id: str) -> ResponseReturnValue:
    """Get Task by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Task.ENTITY_NAME,
            entity_version=str(Task.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Task not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:  # pragma: no cover
        logger.exception("Error getting Task %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@tasks_bp.route("", methods=["GET"])
@validate_querystring(TaskQueryParams)
@tag(["tasks"])
@operation_id("list_tasks")
@validate(
    responses={
        200: (TaskListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_tasks(
    query_args: TaskQueryParams,
) -> ResponseReturnValue:
    """List Tasks with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.priority:
            search_conditions["priority"] = query_args.priority

        if query_args.assignee:
            search_conditions["assignee"] = query_args.assignee

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
                entity_class=Task.ENTITY_NAME,
                condition=condition,
                entity_version=str(Task.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Task.ENTITY_NAME,
                entity_version=str(Task.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing Tasks: %s", str(e))
        return jsonify({"error": str(e)}), 500
