"""
Performance Reports API Routes for Product Performance Analysis System

REST API endpoints for managing PerformanceReport entities including CRUD operations
and report generation triggers as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart_schema import tag, validate_json, validate_querystring

from application.entity.performance_report.version_1.performance_report import (
    PerformanceReport,
)
from services.services import get_entity_service

# Create blueprint for performance report routes
performance_reports_bp = Blueprint(
    "performance_reports", __name__, url_prefix="/api/performance-reports"
)

logger = logging.getLogger(__name__)


@performance_reports_bp.route("/", methods=["POST"])
@tag(["PerformanceReports"])
@validate_json(PerformanceReport)
async def create_performance_report(
    json: PerformanceReport,
) -> tuple[Dict[str, Any], int]:
    """
    Create a new PerformanceReport entity.

    Creates a new performance report that will be processed through the
    report generation and finalization workflow.
    """
    try:
        entity_service = get_entity_service()

        # Convert Pydantic model to dict for EntityService
        report_dict = json.model_dump(by_alias=True)

        # Save the entity using entity constants
        response = await entity_service.save(
            entity=report_dict,
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
        )

        # Return the created entity with technical ID and state
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": report_dict,
        }

        logger.info(f"Created PerformanceReport entity with ID: {response.metadata.id}")
        return result, 201

    except Exception as e:
        logger.error(f"Error creating PerformanceReport entity: {str(e)}")
        return {"error": "Failed to create performance report", "details": str(e)}, 500


@performance_reports_bp.route("/<entity_id>", methods=["GET"])
@tag(["PerformanceReports"])
async def get_performance_report(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Retrieve a PerformanceReport entity by ID.

    Returns the performance report entity with current state and all generated content.
    """
    try:
        entity_service = get_entity_service()

        # Get the entity by technical ID
        response = await entity_service.get(
            entity_id=entity_id,
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
        )

        if not response or not response.entity:
            return {"error": "Performance report not found"}, 404

        # Return the entity with metadata
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": response.entity,
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error retrieving PerformanceReport entity {entity_id}: {str(e)}")
        return {
            "error": "Failed to retrieve performance report",
            "details": str(e),
        }, 500


@performance_reports_bp.route("/<entity_id>", methods=["PUT"])
@tag(["PerformanceReports"])
@validate_json(PerformanceReport)
async def update_performance_report(
    entity_id: str, json: PerformanceReport
) -> tuple[Dict[str, Any], int]:
    """
    Update a PerformanceReport entity.

    Updates the performance report and optionally triggers reprocessing through
    the report generation workflow.
    """
    try:
        entity_service = get_entity_service()

        # Get transition from query parameters (optional)
        transition = request.args.get("transition")

        # Convert Pydantic model to dict for EntityService
        report_dict = json.model_dump(by_alias=True)

        # Update the entity
        if transition:
            response = await entity_service.update_with_transition(
                entity_id=entity_id,
                entity=report_dict,
                entity_class=PerformanceReport.ENTITY_NAME,
                entity_version=str(PerformanceReport.ENTITY_VERSION),
                transition=transition,
            )
        else:
            response = await entity_service.update(
                entity_id=entity_id,
                entity=report_dict,
                entity_class=PerformanceReport.ENTITY_NAME,
                entity_version=str(PerformanceReport.ENTITY_VERSION),
            )

        # Return the updated entity
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": response.entity,
        }

        logger.info(f"Updated PerformanceReport entity {entity_id}")
        return result, 200

    except Exception as e:
        logger.error(f"Error updating PerformanceReport entity {entity_id}: {str(e)}")
        return {"error": "Failed to update performance report", "details": str(e)}, 500


@performance_reports_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["PerformanceReports"])
async def delete_performance_report(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a PerformanceReport entity.

    Removes the performance report entity from the system.
    """
    try:
        entity_service = get_entity_service()

        # Delete the entity
        await entity_service.delete(
            entity_id=entity_id,
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
        )

        logger.info(f"Deleted PerformanceReport entity {entity_id}")
        return {"message": "Performance report deleted successfully"}, 200

    except Exception as e:
        logger.error(f"Error deleting PerformanceReport entity {entity_id}: {str(e)}")
        return {"error": "Failed to delete performance report", "details": str(e)}, 500


@performance_reports_bp.route("/", methods=["GET"])
@tag(["PerformanceReports"])
async def list_performance_reports() -> tuple[Dict[str, Any], int]:
    """
    List PerformanceReport entities with optional filtering.

    Returns a paginated list of performance reports with filtering options.
    """
    try:
        entity_service = get_entity_service()

        # Get query parameters
        page_size = int(request.args.get("page_size", 50))
        page_token = request.args.get("page_token")
        status = request.args.get("status")
        email_sent = request.args.get("email_sent")

        # Build search query
        query = {}
        if status:
            query["reportStatus"] = status
        if email_sent is not None:
            query["emailSent"] = email_sent.lower() == "true"

        # Search for entities
        response = await entity_service.search(
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
            query=query,
            page_size=page_size,
            page_token=page_token,
        )

        # Format response
        entities = []
        if hasattr(response, "entities") and response.entities:
            for entity_data in response.entities:
                entities.append(
                    {
                        "id": entity_data.metadata.id,
                        "state": entity_data.metadata.state,
                        "entity": entity_data.entity,
                    }
                )

        result = {
            "entities": entities,
            "page_token": getattr(response, "next_page_token", None),
            "total_count": len(entities),
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error listing PerformanceReport entities: {str(e)}")
        return {"error": "Failed to list performance reports", "details": str(e)}, 500


@performance_reports_bp.route("/generate-weekly", methods=["POST"])
@tag(["PerformanceReports"])
async def generate_weekly_report() -> tuple[Dict[str, Any], int]:
    """
    Generate a new weekly performance report.

    Creates and triggers the generation of a weekly performance report
    based on current product data.
    """
    try:
        from datetime import datetime, timedelta, timezone

        entity_service = get_entity_service()

        # Calculate report period (last 7 days)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        # Create a new performance report
        report_data = {
            "reportTitle": f"Weekly Product Performance Report - {end_date.strftime('%Y-%m-%d')}",
            "reportPeriodStart": start_date.isoformat().replace("+00:00", "Z"),
            "reportPeriodEnd": end_date.isoformat().replace("+00:00", "Z"),
            "executiveSummary": "Weekly performance analysis pending generation...",
            "reportStatus": "draft",
            "emailSent": False,
        }

        # Save the new report entity
        response = await entity_service.save(
            entity=report_data,
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
        )

        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "message": "Weekly report generation initiated",
            "entity": report_data,
        }

        logger.info(
            f"Initiated weekly report generation with ID: {response.metadata.id}"
        )
        return result, 201

    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return {"error": "Failed to generate weekly report", "details": str(e)}, 500


@performance_reports_bp.route("/latest", methods=["GET"])
@tag(["PerformanceReports"])
async def get_latest_report() -> tuple[Dict[str, Any], int]:
    """
    Get the latest finalized performance report.

    Returns the most recently generated and finalized performance report.
    """
    try:
        entity_service = get_entity_service()

        # Search for finalized reports
        response = await entity_service.search(
            entity_class=PerformanceReport.ENTITY_NAME,
            entity_version=str(PerformanceReport.ENTITY_VERSION),
            query={"reportStatus": "finalized"},
            page_size=100,
        )

        latest_report = None
        latest_timestamp = None

        if hasattr(response, "entities") and response.entities:
            for entity_data in response.entities:
                entity = entity_data.entity
                generation_time = entity.get("generationTimestamp")

                if generation_time and (
                    latest_timestamp is None or generation_time > latest_timestamp
                ):
                    latest_report = {
                        "id": entity_data.metadata.id,
                        "state": entity_data.metadata.state,
                        "entity": entity,
                    }
                    latest_timestamp = generation_time

        if latest_report:
            return latest_report, 200
        else:
            return {"error": "No finalized reports found"}, 404

    except Exception as e:
        logger.error(f"Error getting latest report: {str(e)}")
        return {"error": "Failed to get latest report", "details": str(e)}, 500
