"""
AnalysisReport Routes for Cyoda Client Application

Manages all AnalysisReport-related API endpoints including read operations
and workflow transitions as specified in functional requirements.
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

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

from ..entity.analysis_report.version_1.analysis_report import AnalysisReport
from ..models import (
    AnalysisReportListResponse,
    AnalysisReportQueryParams,
    AnalysisReportResponse,
    AnalysisReportUpdateQueryParams,
    ErrorResponse,
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


analysis_reports_bp = Blueprint(
    "analysis_reports", __name__, url_prefix="/api/analysis-reports"
)


@analysis_reports_bp.route("", methods=["GET"])
@validate_querystring(AnalysisReportQueryParams)
@tag(["analysis-reports"])
@operation_id("list_analysis_reports")
@validate(
    responses={
        200: (AnalysisReportListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_analysis_reports(
    query_args: AnalysisReportQueryParams,
) -> ResponseReturnValue:
    """List AnalysisReports with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.analysis_request_id:
            search_conditions["analysisRequestId"] = query_args.analysis_request_id

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
                entity_class=AnalysisReport.ENTITY_NAME,
                condition=condition,
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=AnalysisReport.ENTITY_NAME,
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.page * query_args.size
        end = start + query_args.size
        paginated_entities = entity_list[start:end]

        # Calculate pagination info
        total_elements = len(entity_list)
        total_pages = (total_elements + query_args.size - 1) // query_args.size

        return (
            jsonify(
                {
                    "content": paginated_entities,
                    "totalElements": total_elements,
                    "totalPages": total_pages,
                    "size": query_args.size,
                    "number": query_args.page,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing AnalysisReports: %s", str(e))
        return jsonify({"error": str(e)}), 500


@analysis_reports_bp.route("/<entity_id>", methods=["GET"])
@tag(["analysis-reports"])
@operation_id("get_analysis_report")
@validate(
    responses={
        200: (AnalysisReportResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_analysis_report(entity_id: str) -> ResponseReturnValue:
    """Get AnalysisReport by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=AnalysisReport.ENTITY_NAME,
            entity_version=str(AnalysisReport.ENTITY_VERSION),
        )

        if not response:
            return {"error": "AnalysisReport not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting AnalysisReport %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@analysis_reports_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(AnalysisReportUpdateQueryParams)
@tag(["analysis-reports"])
@operation_id("update_analysis_report")
@validate(
    request=AnalysisReport,
    responses={
        200: (AnalysisReportResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_analysis_report(
    entity_id: str, data: AnalysisReport, query_args: AnalysisReportUpdateQueryParams
) -> ResponseReturnValue:
    """Update AnalysisReport and optionally trigger workflow transition with validation"""
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
            entity_class=AnalysisReport.ENTITY_NAME,
            transition=transition,
            entity_version=str(AnalysisReport.ENTITY_VERSION),
        )

        logger.info("Updated AnalysisReport %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating AnalysisReport %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating AnalysisReport %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@analysis_reports_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["analysis-reports"])
@operation_id("get_analysis_report_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for AnalysisReport"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=AnalysisReport.ENTITY_NAME,
            entity_version=str(AnalysisReport.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for AnalysisReport %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@analysis_reports_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["analysis-reports"])
@operation_id("trigger_analysis_report_transition")
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
            entity_class=AnalysisReport.ENTITY_NAME,
            entity_version=str(AnalysisReport.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "AnalysisReport not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=AnalysisReport.ENTITY_NAME,
            entity_version=str(AnalysisReport.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on AnalysisReport %s",
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
            "Error executing transition on AnalysisReport %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
