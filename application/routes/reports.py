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

from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service

# Imported for entity constants / typing
from ..entity.report import Report
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ReportListResponse,
    ReportQueryParams,
    ReportResponse,
    ReportSearchResponse,
    ReportUpdateQueryParams,
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

reports_bp = Blueprint(
    "reports", __name__, url_prefix="/api/reports"
)

# ---- Routes -----------------------------------------------------------------

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
async def create_report(
    data: Report,
) -> ResponseReturnValue:
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

        # Return created entity directly (thin proxy)
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
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

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
        200: (ReportListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_reports(
    query_args: ReportQueryParams,
) -> ResponseReturnValue:
    """List Reports with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.report_type:
            search_conditions["reportType"] = query_args.report_type

        if query_args.email_sent is not None:
            search_conditions["emailSent"] = str(query_args.email_sent).lower()

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

        # Apply date filtering if specified
        if query_args.generated_after:
            try:
                from datetime import datetime
                filter_date = datetime.fromisoformat(query_args.generated_after.replace("Z", "+00:00"))
                filtered_entities = []
                for entity in entity_list:
                    generated_at = entity.get("generatedAt")
                    if generated_at:
                        entity_date = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
                        if entity_date >= filter_date:
                            filtered_entities.append(entity)
                entity_list = filtered_entities
            except ValueError:
                logger.warning("Invalid date format in generated_after filter: %s", query_args.generated_after)

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
    """Update Report and optionally trigger workflow transition with validation"""
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
            entity_class=Report.ENTITY_NAME,
            transition=transition,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Updated Report %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating Report %s: %s", entity_id, str(e)
        )
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
    """Delete Report with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

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
