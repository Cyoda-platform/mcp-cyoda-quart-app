"""
Report Routes for Pet Store Performance Analysis System

Manages all Report-related API endpoints including CRUD operations
and workflow transitions for report generation and email delivery.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring
from pydantic import BaseModel, Field

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service
from application.entity.report.version_1.report import Report

logger = logging.getLogger(__name__)


# Request/Response models
class ReportQueryParams(BaseModel):
    report_type: Optional[str] = Field(
        None, alias="reportType", description="Filter by report type"
    )
    email_sent: Optional[bool] = Field(
        None, alias="emailSent", description="Filter by email status"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class ReportUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


class SearchRequest(BaseModel):
    report_type: Optional[str] = Field(None, alias="reportType")
    email_recipient: Optional[str] = Field(None, alias="emailRecipient")
    email_sent: Optional[bool] = Field(None, alias="emailSent")


class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None


class DeleteResponse(BaseModel):
    success: bool
    message: str
    entity_id: str


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


# Create blueprint
reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("", methods=["POST"])
@tag(["reports"])
@operation_id("create_report")
@validate(
    request=Report,
    responses={
        201: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_report(data: Report) -> ResponseReturnValue:
    """Create a new Report entity"""
    try:
        entity_data = data.model_dump(by_alias=True)

        entity_service = get_entity_service()
        response = await entity_service.save(
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
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_report(entity_id: str) -> ResponseReturnValue:
    """Get Report by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        response = await entity_service.get_by_id(
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
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_reports(query_args: ReportQueryParams) -> ResponseReturnValue:
    """List Reports with optional filtering"""
    try:
        entity_service = get_entity_service()
        search_conditions: Dict[str, str] = {}

        if query_args.report_type:
            search_conditions["reportType"] = query_args.report_type
        if query_args.email_sent is not None:
            search_conditions["emailSent"] = str(query_args.email_sent).lower()
        if query_args.state:
            search_conditions["state"] = query_args.state

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await entity_service.search(
                entity_class=Report.ENTITY_NAME,
                condition=condition,
                entity_version=str(Report.ENTITY_VERSION),
            )
        else:
            entities = await entity_service.find_all(
                entity_class=Report.ENTITY_NAME,
                entity_version=str(Report.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

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
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_report(
    entity_id: str, data: Report, query_args: ReportUpdateQueryParams
) -> ResponseReturnValue:
    """Update Report and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await entity_service.update(
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
    """Delete Report"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        await entity_service.delete_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Deleted Report %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="Report deleted successfully",
            entity_id=entity_id,
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
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_reports(data: SearchRequest) -> ResponseReturnValue:
    """Search Reports using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        entity_service = get_entity_service()
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(
            entity_class=Report.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Report.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Reports: %s", str(e))
        return {"error": str(e)}, 500
