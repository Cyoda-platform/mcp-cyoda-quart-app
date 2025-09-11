"""
CommentAnalysisReport Routes for Cyoda Client Application

Manages all CommentAnalysisReport-related API endpoints for retrieving reports,
resending emails, and downloading report content as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from quart import Blueprint, Response, jsonify
from quart.typing import ResponseReturnValue

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)

comment_analysis_reports_bp = Blueprint("comment_analysis_reports", __name__)


# ---- Service typing ---------------------------------------------------------


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...

    def get_state(self) -> str: ...

    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...

    async def execute_transition(
        self,
        *,
        entity_id: str,
        transition: str,
        entity_class: str,
        entity_version: str,
    ) -> _SavedEntity: ...


# Services will be accessed through the registry
entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Routes -----------------------------------------------------------------


@comment_analysis_reports_bp.route(
    "/api/comment-analysis-requests/<request_id>/report", methods=["GET"]
)
async def get_analysis_report(request_id: str) -> ResponseReturnValue:
    """Retrieve the analysis report for a specific request"""
    try:
        service = get_services()

        # Build search condition to find report for this request
        condition = (
            SearchConditionRequest.builder()
            .equals("analysisRequestId", request_id)
            .build()
        )

        reports = await service.search(
            entity_class="CommentAnalysisReport",
            condition=condition,
            entity_version="1",
        )

        if not reports:
            return jsonify({"error": "Analysis report not found"}), 404

        # Get the first (and should be only) report
        report = reports[0]

        # Convert to API response format
        report_data = {
            "id": report.get_id(),
            "analysisRequestId": report.data.get("analysisRequestId"),
            "totalComments": report.data.get("totalComments"),
            "positiveComments": report.data.get("positiveComments"),
            "negativeComments": report.data.get("negativeComments"),
            "neutralComments": report.data.get("neutralComments"),
            "averageWordCount": report.data.get("averageWordCount"),
            "topCommenterEmail": report.data.get("topCommenterEmail"),
            "reportContent": report.data.get("reportContent"),
            "state": report.get_state(),
            "generatedAt": report.data.get("generatedAt"),
            "sentAt": report.data.get("sentAt"),
        }

        return jsonify(report_data), 200

    except Exception as e:
        logger.exception("Error getting report for request %s: %s", request_id, str(e))
        return jsonify({"error": str(e)}), 500


@comment_analysis_reports_bp.route("/api/reports/<entity_id>/resend", methods=["PUT"])
async def resend_report_email(entity_id: str) -> ResponseReturnValue:
    """Resend a failed report via email"""
    try:
        service = get_services()

        # Execute manual transition from FAILED_TO_SEND to GENERATED
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_retry",
            entity_class="CommentAnalysisReport",
            entity_version="1",
        )

        logger.info("Resending report email for CommentAnalysisReport %s", entity_id)

        # Convert to API response format
        report_data = {
            "id": response.metadata.id,
            "analysisRequestId": response.data.get("analysisRequestId"),
            "totalComments": response.data.get("totalComments"),
            "positiveComments": response.data.get("positiveComments"),
            "negativeComments": response.data.get("negativeComments"),
            "neutralComments": response.data.get("neutralComments"),
            "averageWordCount": response.data.get("averageWordCount"),
            "topCommenterEmail": response.data.get("topCommenterEmail"),
            "reportContent": response.data.get("reportContent"),
            "state": response.metadata.state,
            "generatedAt": response.data.get("generatedAt"),
            "sentAt": response.data.get("sentAt"),
        }

        return jsonify(report_data), 200

    except Exception as e:
        logger.exception("Error resending report %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@comment_analysis_reports_bp.route("/api/reports/<entity_id>/download", methods=["GET"])
async def download_report(entity_id: str) -> ResponseReturnValue:
    """Download the report content as a text file"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class="CommentAnalysisReport",
            entity_version="1",
        )

        if not response:
            return jsonify({"error": "Report not found"}), 404

        # Get report content
        report_content = response.data.get("reportContent", "")
        analysis_request_id = response.data.get("analysisRequestId", "unknown")

        # Create filename
        filename = f"comment_analysis_report_{analysis_request_id}.txt"

        # Return as downloadable text file
        return Response(
            report_content,
            mimetype="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/plain; charset=utf-8",
            },
        )

    except Exception as e:
        logger.exception("Error downloading report %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
