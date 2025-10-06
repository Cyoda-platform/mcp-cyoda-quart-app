"""
Report Routes for Booking Data Analysis

Manages all Report-related API endpoints including CRUD operations,
report generation, and display formatting as specified in functional requirements.
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
from ..entity.report import Report
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
from ..models.request_models import ReportGenerationRequest
from ..models.response_models import ReportDisplayResponse

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
    """Create a new Report entity"""
    try:
        entity_service = get_entity_service()
        
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await entity_service.save(
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


@reports_bp.route("/generate", methods=["POST"])
@tag(["reports"])
@operation_id("generate_report")
@validate(
    request=ReportGenerationRequest,
    responses={
        201: (ReportResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def generate_report(data: ReportGenerationRequest) -> ResponseReturnValue:
    """Generate a new report with specified criteria"""
    try:
        entity_service = get_entity_service()
        
        # Create Report entity from generation request
        report = Report(
            title=data.title,
            description=data.description,
            report_type=data.report_type,
            display_format=data.display_format,
            filter_criteria=data.filter_criteria,
            summary=None,  # Will be populated by processor
            booking_count=0,  # Will be populated by processor
        )

        # Convert to entity data
        entity_data = report.model_dump(by_alias=True)

        # Save the entity (workflow will handle generation)
        response = await entity_service.save(
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Generated Report with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error generating Report: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error generating Report: %s", str(e))
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
    """Get Report by ID"""
    try:
        entity_service = get_entity_service()
        
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await entity_service.get_by_id(
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


@reports_bp.route("/<entity_id>/display", methods=["GET"])
@tag(["reports"])
@operation_id("get_report_display")
@validate(
    responses={
        200: (ReportDisplayResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_report_display(entity_id: str) -> ResponseReturnValue:
    """Get Report in user-friendly display format"""
    try:
        entity_service = get_entity_service()
        
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await entity_service.get_by_id(
            entity_id=entity_id,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Report not found", "code": "NOT_FOUND"}, 404

        # Convert to Report entity and get display format
        report_data = response.data
        if isinstance(report_data, dict):
            report = Report(**report_data)
        else:
            report = report_data

        # Return in display format
        display_data = report.to_display_format()
        return jsonify(display_data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Report display %s: %s", entity_id, str(e))
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
    """List Reports with optional filtering"""
    try:
        entity_service = get_entity_service()
        
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.report_type:
            search_conditions["reportType"] = query_args.report_type

        if query_args.display_format:
            search_conditions["displayFormat"] = query_args.display_format

        if query_args.generated_by:
            search_conditions["generatedBy"] = query_args.generated_by

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
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

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Reports: %s", str(e))
        return jsonify({"error": str(e)}), 500


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
    """Update Report and optionally trigger workflow transition"""
    try:
        entity_service = get_entity_service()

        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await entity_service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            transition=transition,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Updated Report %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Report %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Report %s: %s", entity_id, str(e))
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
    """Delete Report"""
    try:
        entity_service = get_entity_service()

        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await entity_service.delete_by_id(
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


# Additional endpoints for report operations

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
    """Search Reports using field-value search"""
    try:
        entity_service = get_entity_service()

        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(
            entity_class=Report.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Report.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

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
        entity_service = get_entity_service()

        count = await entity_service.count(
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        response = CountResponse(count=count, entity_type="Report")
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Reports: %s", str(e))
        return jsonify({"error": str(e)}), 500
