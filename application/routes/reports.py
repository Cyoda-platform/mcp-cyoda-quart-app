"""
Report Routes for Pet Store Performance Analysis System

Manages all Report-related API endpoints including CRUD operations
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

# Import entity and models
from ..entity.report.version_1.report import Report
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    ReportListResponse,
    ReportQueryParams,
    ReportResponse,
    ReportSearchResponse,
    ReportUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


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
    request=Report,
    responses={
        201: (ReportResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_report(data: Report) -> ResponseReturnValue:
    """Create a new Report with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
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
@validate(
    responses={
        200: (ReportResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_report(entity_id: str) -> ResponseReturnValue:
    """Get Report by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

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
    """List Reports with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.report_type:
            search_conditions["reportType"] = query_args.report_type
        if query_args.email_status:
            search_conditions["emailStatus"] = query_args.email_status
        if query_args.state:
            search_conditions["state"] = query_args.state

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

        # Convert to list and apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply date filtering if specified
        if query_args.period_start or query_args.period_end:
            filtered_list = []
            for entity in entity_list:
                period_start = entity.get("reportPeriodStart")
                period_end = entity.get("reportPeriodEnd")

                if (
                    query_args.period_start
                    and period_start
                    and period_start < query_args.period_start
                ):
                    continue
                if (
                    query_args.period_end
                    and period_end
                    and period_end > query_args.period_end
                ):
                    continue

                filtered_list.append(entity)
            entity_list = filtered_list

        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"reports": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Reports: %s", str(e))
        return {"error": str(e)}, 500


@reports_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(ReportUpdateQueryParams)
@tag(["reports"])
@operation_id("update_report")
@validate(
    request=Report,
    responses={
        200: (ReportResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_report(
    entity_id: str, data: Report, query_args: ReportUpdateQueryParams
) -> ResponseReturnValue:
    """Update Report and optionally trigger workflow transition with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
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
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_report(entity_id: str) -> ResponseReturnValue:
    """Delete Report with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Deleted Report %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Report deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/search", methods=["POST"])
@tag(["reports"])
@operation_id("search_reports")
@validate(
    request=SearchRequest,
    responses={
        200: (ReportSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_reports(data: SearchRequest) -> ResponseReturnValue:
    """Search Reports using field-value search with validation"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Report.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Report.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"reports": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Reports: %s", str(e))
        return {"error": str(e)}, 500


@reports_bp.route("/count", methods=["GET"])
@tag(["reports"])
@operation_id("count_reports")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_reports() -> ResponseReturnValue:
    """Count total number of Reports"""
    try:
        count = await service.count(
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting Reports: %s", str(e))
        return {"error": str(e)}, 500


@reports_bp.route("/<entity_id>/content", methods=["GET"])
@tag(["reports"])
@operation_id("get_report_content")
@validate(
    responses={
        200: (dict, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_report_content(entity_id: str) -> ResponseReturnValue:
    """Get Report content (HTML/JSON) for viewing or download"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Report not found", "code": "NOT_FOUND"}, 404

        report_data = _to_entity_dict(response.data)
        content = report_data.get("reportContent")

        if not content:
            return {"error": "Report content not available", "code": "NO_CONTENT"}, 404

        return {
            "content": content,
            "format": report_data.get("reportFormat", "HTML"),
            "title": report_data.get("reportTitle"),
            "generated_at": report_data.get("generatedAt"),
        }, 200

    except Exception as e:
        logger.exception("Error getting Report content %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
