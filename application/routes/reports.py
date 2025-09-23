"""
Report Routes for Product Performance Analysis and Reporting System

Manages all Report-related API endpoints including CRUD operations
and workflow transitions following the thin proxy pattern.
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


# Request/Response models
class ReportQueryParams(BaseModel):
    """Query parameters for listing reports"""
    report_type: Optional[str] = Field(None, description="Filter by report type")
    email_status: Optional[str] = Field(None, description="Filter by email status")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for updating reports"""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class WeeklyReportRequest(BaseModel):
    """Request model for creating weekly reports"""
    report_period: str = Field(..., description="Report period (e.g., '2024-01-01 to 2024-01-07')")
    email_recipient: str = Field(
        default="victoria.sagdieva@cyoda.com", 
        description="Email recipient for the report"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class DeleteResponse(BaseModel):
    """Delete response model"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


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
        201: (Report, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_report(data: Report) -> ResponseReturnValue:
    """Create a new Report entity"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Created Report with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Report: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Report: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/weekly", methods=["POST"])
@tag(["reports"])
@operation_id("create_weekly_report")
@validate(
    request=WeeklyReportRequest,
    responses={
        201: (Report, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_weekly_report(data: WeeklyReportRequest) -> ResponseReturnValue:
    """Create a new weekly performance report"""
    try:
        from datetime import datetime, timezone
        
        # Create Report entity for weekly report
        report_data = {
            "reportTitle": f"Weekly Pet Store Performance Report - {data.report_period}",
            "reportType": "weekly",
            "reportPeriod": data.report_period,
            "emailRecipient": data.email_recipient,
            "emailSubject": f"Weekly Pet Store Performance Report - {data.report_period}",
            "dataSource": "Pet Store API",
        }

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=report_data,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Created Weekly Report with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Weekly Report: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Weekly Report: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/<entity_id>", methods=["GET"])
@tag(["reports"])
@operation_id("get_report")
@validate(
    responses={
        200: (Report, None),
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

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Report not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
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
        service = get_entity_service()
        
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.report_type:
            search_conditions["reportType"] = query_args.report_type

        if query_args.email_status:
            search_conditions["emailStatus"] = query_args.email_status

        # Get entities
        if search_conditions:
            # Build search condition request
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

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
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
        200: (Report, None),
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

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            transition=transition,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Updated Report %s", entity_id)

        # Return updated entity directly (thin proxy)
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

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Deleted Report %s", entity_id)

        # Thin proxy: return success message
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
