"""
Report Routes for Pet Store Performance Analysis System

Manages all Report-related API endpoints including CRUD operations
and workflow transitions for automated report generation and email dispatch.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.report.version_1.report import Report
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("", methods=["POST"])
@tag(["reports"])
@operation_id("create_report")
async def create_report() -> ResponseReturnValue:
    """Create a new Report entity"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Create Report entity from request data
        report = Report(**data)
        entity_data = report.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Created Report with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Report: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Report: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/<entity_id>", methods=["GET"])
@tag(["reports"])
@operation_id("get_report")
async def get_report(entity_id: str) -> ResponseReturnValue:
    """Get Report by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Report not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("", methods=["GET"])
@tag(["reports"])
@operation_id("list_reports")
async def list_reports() -> ResponseReturnValue:
    """List Reports with optional filtering"""
    try:
        # Get query parameters
        report_type = request.args.get("report_type")
        email_status = request.args.get("email_status")
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 50))

        service = get_entity_service()

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if report_type:
            search_conditions["reportType"] = report_type
        if email_status:
            search_conditions["emailStatus"] = email_status

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Report.ENTITY_NAME,
                condition=condition,
                entity_version=str(Report.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Report.ENTITY_NAME,
                entity_version=str(Report.ENTITY_VERSION),
            )

        # Apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]
        paginated_entities = entity_list[offset : offset + limit]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Reports: %s", str(e))
        return {"error": str(e)}, 500


@reports_bp.route("/<entity_id>", methods=["PUT"])
@tag(["reports"])
@operation_id("update_report")
async def update_report(entity_id: str) -> ResponseReturnValue:
    """Update Report and optionally trigger workflow transition"""
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
            entity_class=Report.ENTITY_NAME,
            transition=transition,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Updated Report %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["reports"])
@operation_id("delete_report")
async def delete_report(entity_id: str) -> ResponseReturnValue:
    """Delete Report"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Deleted Report %s", entity_id)
        return {
            "success": True,
            "message": "Report deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/search", methods=["POST"])
@tag(["reports"])
@operation_id("search_reports")
async def search_reports() -> ResponseReturnValue:
    """Search Reports using field-value conditions"""
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
            entity_class=Report.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Report.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Reports: %s", str(e))
        return {"error": str(e)}, 500


@reports_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["reports"])
@operation_id("trigger_report_transition")
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
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "Report not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data["transition_name"],
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Report %s", data["transition_name"], entity_id
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception(
            "Error executing transition on Report %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500
