"""
DataExtraction Routes for Product Performance Analysis and Reporting System

Manages all DataExtraction-related API endpoints including CRUD operations
and extraction scheduling as specified in functional requirements.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
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


data_extractions_bp = Blueprint(
    "data_extractions", __name__, url_prefix="/api/data-extractions"
)


@data_extractions_bp.route("", methods=["POST"])
@tag(["data-extractions"])
@operation_id("create_data_extraction")
async def create_data_extraction() -> ResponseReturnValue:
    """Create a new DataExtraction entity"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Create DataExtraction entity
        extraction = DataExtraction(**data)
        entity_data = extraction.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Created DataExtraction with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["GET"])
@tag(["data-extractions"])
@operation_id("get_data_extraction")
async def get_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Get DataExtraction by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        if not response:
            return {"error": "DataExtraction not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("", methods=["GET"])
@tag(["data-extractions"])
@operation_id("list_data_extractions")
async def list_data_extractions() -> ResponseReturnValue:
    """List DataExtractions with optional filtering"""
    try:
        # Get query parameters
        extraction_type = request.args.get("extraction_type")
        schedule_pattern = request.args.get("schedule_pattern")
        state = request.args.get("state")
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if extraction_type:
            search_conditions["extractionType"] = extraction_type
        if schedule_pattern:
            search_conditions["schedulePattern"] = schedule_pattern
        if state:
            search_conditions["state"] = state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=DataExtraction.ENTITY_NAME,
                condition=condition,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=DataExtraction.ENTITY_NAME,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )

        # Apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]
        total = len(entity_list)
        paginated_entities = entity_list[offset : offset + limit]

        return (
            jsonify(
                {
                    "extractions": paginated_entities,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing DataExtractions: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["PUT"])
@tag(["data-extractions"])
@operation_id("update_data_extraction")
async def update_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Update DataExtraction and optionally trigger workflow transition"""
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
            entity_class=DataExtraction.ENTITY_NAME,
            transition=transition,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Updated DataExtraction %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating DataExtraction %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["data-extractions"])
@operation_id("delete_data_extraction")
async def delete_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Delete DataExtraction"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Deleted DataExtraction %s", entity_id)
        return {
            "success": True,
            "message": "DataExtraction deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>/execute", methods=["POST"])
@tag(["data-extractions"])
@operation_id("execute_data_extraction")
async def execute_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Trigger data extraction execution"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Trigger start_extraction transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="start_extraction",
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Triggered execution for DataExtraction %s", entity_id)
        return {
            "id": response.metadata.id,
            "message": "Data extraction execution triggered successfully",
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error executing DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/schedule/weekly", methods=["POST"])
@tag(["data-extractions"])
@operation_id("schedule_weekly_extraction")
async def schedule_weekly_extraction() -> ResponseReturnValue:
    """Schedule a weekly data extraction for Mondays"""
    try:
        # Calculate next Monday
        now = datetime.now(timezone.utc)
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:  # If today is Monday
            days_until_monday = 7  # Schedule for next Monday

        next_monday = now + timedelta(days=days_until_monday)
        next_monday = next_monday.replace(
            hour=9, minute=0, second=0, microsecond=0
        )  # 9 AM UTC

        # Create extraction data
        extraction = DataExtraction(
            extraction_type="pet_store_products",
            source_url="https://petstore.swagger.io/v2",
            schedule_pattern="weekly_monday",
            scheduled_for=next_monday.isoformat().replace("+00:00", "Z"),
            extraction_config={"auto_analyze": True, "create_report": True}
        )
        entity_data = extraction.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        extraction_id = response.metadata.id
        logger.info(
            "Scheduled weekly DataExtraction with ID: %s for %s",
            extraction_id,
            next_monday,
        )

        return {
            "id": extraction_id,
            "message": "Weekly data extraction scheduled successfully",
            "scheduled_for": next_monday.isoformat().replace("+00:00", "Z"),
            "schedule_pattern": "weekly_monday",
        }, 201

    except Exception as e:
        logger.exception("Error scheduling weekly extraction: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/status", methods=["GET"])
@tag(["data-extractions"])
@operation_id("get_extraction_status")
async def get_extraction_status() -> ResponseReturnValue:
    """Get status summary of all data extractions"""
    try:
        # Get all extractions
        entities = await service.find_all(
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        extractions = [_to_entity_dict(r.data) for r in entities]

        # Calculate status metrics
        total_extractions = len(extractions)
        completed_extractions = len(
            [e for e in extractions if e.get("state") == "completed"]
        )
        failed_extractions = len([e for e in extractions if e.get("state") == "failed"])
        scheduled_extractions = len(
            [e for e in extractions if e.get("state") == "scheduled"]
        )

        # Get recent extractions
        recent_extractions = sorted(
            extractions, key=lambda e: e.get("createdAt", ""), reverse=True
        )[:5]

        status_summary = {
            "total_extractions": total_extractions,
            "completed_extractions": completed_extractions,
            "failed_extractions": failed_extractions,
            "scheduled_extractions": scheduled_extractions,
            "success_rate": (
                (completed_extractions / total_extractions * 100)
                if total_extractions > 0
                else 0
            ),
            "recent_extractions": recent_extractions,
        }

        return status_summary, 200

    except Exception as e:
        logger.exception("Error getting extraction status: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/manual", methods=["POST"])
@tag(["data-extractions"])
@operation_id("trigger_manual_extraction")
async def trigger_manual_extraction() -> ResponseReturnValue:
    """Trigger a manual data extraction immediately"""
    try:
        # Create manual extraction
        extraction_data = {
            "extraction_type": "pet_store_products",
            "source_url": "https://petstore.swagger.io/v2",
            "schedule_pattern": "manual",
            "scheduled_for": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

        extraction = DataExtraction(**extraction_data)
        entity_data = extraction.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        extraction_id = response.metadata.id
        logger.info("Created manual DataExtraction with ID: %s", extraction_id)

        # Trigger execution immediately
        await service.execute_transition(
            entity_id=extraction_id,
            transition="start_extraction",
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        return {
            "id": extraction_id,
            "message": "Manual data extraction triggered successfully",
            "extraction_type": "pet_store_products",
        }, 201

    except Exception as e:
        logger.exception("Error triggering manual extraction: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
