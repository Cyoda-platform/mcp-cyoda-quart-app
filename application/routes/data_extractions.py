"""
DataExtraction Routes for Pet Store Performance Analysis System

Manages all DataExtraction-related API endpoints including CRUD operations
and workflow transitions for automated data collection from Pet Store API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


data_extractions_bp = Blueprint(
    "data_extractions", __name__, url_prefix="/api/data-extractions"
)


@data_extractions_bp.route("", methods=["POST"])
@tag(["data-extractions"])
@operation_id("create_data_extraction")
async def create_data_extraction() -> ResponseReturnValue:
    """Create a new DataExtraction entity"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Create DataExtraction entity from request data
        extraction = DataExtraction(**data)
        entity_data = extraction.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Created DataExtraction with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["GET"])
@tag(["data-extractions"])
@operation_id("get_data_extraction")
async def get_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Get DataExtraction by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        if not response:
            return {"error": "DataExtraction not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("", methods=["GET"])
@tag(["data-extractions"])
@operation_id("list_data_extractions")
async def list_data_extractions() -> ResponseReturnValue:
    """List DataExtractions with optional filtering"""
    try:
        # Get query parameters
        extraction_type = request.args.get("extraction_type")
        execution_status = request.args.get("execution_status")
        scheduled_day = request.args.get("scheduled_day")
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 50))

        service = get_entity_service()

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if extraction_type:
            search_conditions["extractionType"] = extraction_type
        if execution_status:
            search_conditions["executionStatus"] = execution_status
        if scheduled_day:
            search_conditions["scheduledDay"] = scheduled_day

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=DataExtraction.ENTITY_NAME,
                condition=condition,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=DataExtraction.ENTITY_NAME,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )

        # Apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]
        paginated_entities = entity_list[offset : offset + limit]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/<entity_id>", methods=["PUT"])
@tag(["data-extractions"])
@operation_id("update_data_extraction")
async def update_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Update DataExtraction and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Get transition from query parameters
        transition = request.args.get("transition")

        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=DataExtraction.ENTITY_NAME,
            transition=transition,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Updated DataExtraction %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating DataExtraction %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["data-extractions"])
@operation_id("delete_data_extraction")
async def delete_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Delete DataExtraction"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Deleted DataExtraction %s", entity_id)
        return {
            "success": True,
            "message": "DataExtraction deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/search", methods=["POST"])
@tag(["data-extractions"])
@operation_id("search_data_extractions")
async def search_data_extractions() -> ResponseReturnValue:
    """Search DataExtractions using field-value conditions"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        service = get_entity_service()
        builder = SearchConditionRequest.builder()
        for field, value in data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=DataExtraction.ENTITY_NAME,
            condition=search_request,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["data-extractions"])
@operation_id("trigger_data_extraction_transition")
async def trigger_transition(entity_id: str) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        data = await request.get_json()
        if not data or "transition_name" not in data:
            return {
                "error": "Transition name is required",
                "code": "MISSING_TRANSITION",
            }, 400

        service = get_entity_service()

        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "DataExtraction not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data["transition_name"],
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on DataExtraction %s",
            data["transition_name"],
            entity_id,
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception(
            "Error executing transition on DataExtraction %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500
