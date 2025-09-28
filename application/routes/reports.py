"""
CommentAnalysisReport Routes for Cyoda Client Application

Manages all CommentAnalysisReport-related API endpoints including CRUD operations,
workflow transitions, and report generation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from application.models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    ReportListResponse,
    ReportQueryParams,
    ReportResponse,
    ReportUpdateQueryParams,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("", methods=["POST"])
@tag(["reports"])
@operation_id("create_report")
@validate(
    request=CommentAnalysisReport,
    responses={
        201: (ReportResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_report(data: CommentAnalysisReport) -> ResponseReturnValue:
    """Create a new CommentAnalysisReport with validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        logger.info("Created CommentAnalysisReport with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating CommentAnalysisReport: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating CommentAnalysisReport: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/<entity_id>", methods=["GET"])
@tag(["reports"])
@operation_id("get_report")
@validate(
    responses={
        200: (ReportResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_report(entity_id: str) -> ResponseReturnValue:
    """Get CommentAnalysisReport by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        if not response:
            return {
                "error": "CommentAnalysisReport not found",
                "code": "NOT_FOUND",
            }, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception(
            "Error getting CommentAnalysisReport %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("", methods=["GET"])
@validate_querystring(ReportQueryParams)
@tag(["reports"])
@operation_id("list_reports")
@validate(
    responses={
        200: (ReportListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_reports(query_args: ReportQueryParams) -> ResponseReturnValue:
    """List CommentAnalysisReports with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.post_id is not None:
            search_conditions["postId"] = str(query_args.post_id)

        if query_args.email_sent is not None:
            search_conditions["emailSent"] = str(query_args.email_sent).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=CommentAnalysisReport.ENTITY_NAME,
                condition=condition,
                entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=CommentAnalysisReport.ENTITY_NAME,
                entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
            )

        # Convert to list and apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"reports": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing CommentAnalysisReports: %s", str(e))
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(ReportUpdateQueryParams)
@tag(["reports"])
@operation_id("update_report")
@validate(
    request=CommentAnalysisReport,
    responses={
        200: (ReportResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_report(
    entity_id: str, data: CommentAnalysisReport, query_args: ReportUpdateQueryParams
) -> ResponseReturnValue:
    """Update CommentAnalysisReport and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            transition=transition,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        logger.info("Updated CommentAnalysisReport %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating CommentAnalysisReport %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception(
            "Error updating CommentAnalysisReport %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@reports_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["reports"])
@operation_id("delete_report")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_report(entity_id: str) -> ResponseReturnValue:
    """Delete CommentAnalysisReport with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        logger.info("Deleted CommentAnalysisReport %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="CommentAnalysisReport deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception(
            "Error deleting CommentAnalysisReport %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# Additional endpoints
@reports_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["reports"])
@operation_id("check_report_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if CommentAnalysisReport exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entityId=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking CommentAnalysisReport existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@reports_bp.route("/count", methods=["GET"])
@tag(["reports"])
@operation_id("count_reports")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of CommentAnalysisReports"""
    try:
        count = await service.count(
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting CommentAnalysisReports: %s", str(e))
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["reports"])
@operation_id("get_report_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for CommentAnalysisReport"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entityId=entity_id,
            availableTransitions=transitions,
            currentState=None,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for CommentAnalysisReport %s: %s",
            entity_id,
            str(e),
        )
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["reports"])
@operation_id("trigger_report_transition")
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
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "CommentAnalysisReport not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on CommentAnalysisReport %s",
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
            "Error executing transition on CommentAnalysisReport %s: %s",
            entity_id,
            str(e),
        )
        return jsonify({"error": str(e)}), 500
