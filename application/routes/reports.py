"""
Report Routes for Product Performance Analysis and Reporting System

Manages all Report-related API endpoints including CRUD operations
and email delivery as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.report.version_1.report import Report
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    """Helper to normalize entity data from service"""
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

        # Create Report entity
        report = Report(**data)
        entity_data = report.model_dump(by_alias=True)

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
async def get_report(entity_id: str) -> ResponseReturnValue:
    """Get Report by ID"""
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
@tag(["reports"])
@operation_id("list_reports")
async def list_reports() -> ResponseReturnValue:
    """List Reports with optional filtering"""
    try:
        # Get query parameters
        report_type = request.args.get("report_type")
        email_sent = request.args.get("email_sent", type=bool)
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if report_type:
            search_conditions["reportType"] = report_type
        if email_sent is not None:
            search_conditions["emailSent"] = str(email_sent).lower()

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
        total = len(entity_list)
        paginated_entities = entity_list[offset : offset + limit]

        return (
            jsonify(
                {
                    "reports": paginated_entities,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing Reports: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


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

        # Update the entity
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


@reports_bp.route("/<entity_id>/generate", methods=["POST"])
@tag(["reports"])
@operation_id("generate_report")
async def generate_report(entity_id: str) -> ResponseReturnValue:
    """Trigger report generation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Trigger generate transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="generate",
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Triggered generation for Report %s", entity_id)
        return {
            "id": response.metadata.id,
            "message": "Report generation triggered successfully",
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error generating Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/<entity_id>/email", methods=["POST"])
@tag(["reports"])
@operation_id("email_report")
async def email_report(entity_id: str) -> ResponseReturnValue:
    """Trigger report email delivery"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Trigger send_email transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="send_email",
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        logger.info("Triggered email delivery for Report %s", entity_id)
        return {
            "id": response.metadata.id,
            "message": "Report email delivery triggered successfully",
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error emailing Report %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/weekly", methods=["POST"])
@tag(["reports"])
@operation_id("create_weekly_report")
async def create_weekly_report() -> ResponseReturnValue:
    """Create and generate a weekly performance report"""
    try:
        # Create a new weekly report
        report = Report(
            title="Weekly Product Performance Report",
            reportType="weekly_performance",
            emailRecipients=["victoria.sagdieva@cyoda.com"]
        )
        entity_data = report.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        report_id = response.metadata.id
        logger.info("Created weekly Report with ID: %s", report_id)

        # Trigger generation
        await service.execute_transition(
            entity_id=report_id,
            transition="generate",
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        return {
            "id": report_id,
            "message": "Weekly report created and generation triggered",
            "title": report_data["title"],
        }, 201

    except Exception as e:
        logger.exception("Error creating weekly report: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@reports_bp.route("/summary", methods=["GET"])
@tag(["reports"])
@operation_id("get_reports_summary")
async def get_reports_summary() -> ResponseReturnValue:
    """Get summary of all reports"""
    try:
        # Get all reports
        entities = await service.find_all(
            entity_class=Report.ENTITY_NAME,
            entity_version=str(Report.ENTITY_VERSION),
        )

        reports = [_to_entity_dict(r.data) for r in entities]

        # Calculate summary metrics
        total_reports = len(reports)
        emailed_reports = len([r for r in reports if r.get("emailSent", False)])
        pending_reports = len(
            [r for r in reports if r.get("state") in ["generating", "generated"]]
        )

        summary = {
            "total_reports": total_reports,
            "emailed_reports": emailed_reports,
            "pending_reports": pending_reports,
            "recent_reports": sorted(
                reports, key=lambda r: r.get("createdAt", ""), reverse=True
            )[:5],
        }

        return summary, 200

    except Exception as e:
        logger.exception("Error getting reports summary: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
