"""
WeeklySchedule routes for the cat fact subscription system.
"""

import logging
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from quart import Blueprint, abort, jsonify, request
from quart_schema import validate_request, validate_querystring

from common.config.config import ENTITY_VERSION
from service.services import get_auth_service, get_entity_service

logger = logging.getLogger(__name__)

weeklyschedule_bp = Blueprint(
    "weekly_schedules", __name__, url_prefix="/api/weekly-schedules"
)


class WeeklyScheduleCreateRequest(BaseModel):
    """Request model for creating a weekly schedule."""

    weekStartDate: date
    scheduledDate: datetime


class WeeklyScheduleTransitionRequest(BaseModel):
    """Request model for weekly schedule transitions."""

    transitionName: str


class WeeklyScheduleQuery(BaseModel):
    """Query parameters for listing weekly schedules."""

    state: Optional[str] = None
    page: int = 0
    size: int = 20


def get_services():
    """Get services from the registry lazily."""
    return get_entity_service(), get_auth_service()


@weeklyschedule_bp.route("", methods=["POST"])
@validate_request(WeeklyScheduleCreateRequest)
async def create_weeklyschedule():
    """Create a new weekly schedule."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Create weekly schedule entity data
        schedule_data = {
            "weekStartDate": data["weekStartDate"].isoformat(),
            "scheduledDate": data["scheduledDate"].isoformat(),
        }

        # Save weekly schedule (triggers initial → created transition automatically)
        response = await entity_service.save(
            schedule_data, "weeklyschedule", ENTITY_VERSION
        )

        result = {
            "id": response.technical_id,
            "weekStartDate": response.data.get("weekStartDate"),
            "weekEndDate": response.data.get("weekEndDate"),
            "scheduledDate": response.data.get("scheduledDate"),
            "subscriberCount": response.data.get("subscriberCount"),
            "state": response.state,
        }

        return jsonify(result), 201

    except Exception as e:
        logger.exception(f"Failed to create weekly schedule: {e}")
        return jsonify({"error": "Failed to create weekly schedule"}), 500


@weeklyschedule_bp.route("/<schedule_id>", methods=["GET"])
async def get_weeklyschedule(schedule_id: str):
    """Get weekly schedule details by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        response = await entity_service.get_by_id(
            schedule_id, "weeklyschedule", ENTITY_VERSION
        )

        result = {
            "id": response.technical_id,
            "weekStartDate": response.data.get("weekStartDate"),
            "weekEndDate": response.data.get("weekEndDate"),
            "catFactId": response.data.get("catFactId"),
            "scheduledDate": response.data.get("scheduledDate"),
            "executedDate": response.data.get("executedDate"),
            "subscriberCount": response.data.get("subscriberCount"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get weekly schedule {schedule_id}: {e}")
        abort(404)


@weeklyschedule_bp.route("/<schedule_id>/execute", methods=["PUT"])
@validate_json(WeeklyScheduleTransitionRequest)
async def execute_weeklyschedule(schedule_id: str):
    """Manually execute weekly schedule."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current weekly schedule
        current_response = await entity_service.get_by_id(
            schedule_id, "weeklyschedule", ENTITY_VERSION
        )

        # Update with execution transition
        response = await entity_service.update(
            schedule_id,
            current_response.data,
            "weeklyschedule",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION,
        )

        result = {
            "id": response.technical_id,
            "catFactId": response.data.get("catFactId"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to execute weekly schedule {schedule_id}: {e}")
        return jsonify({"error": "Failed to execute weekly schedule"}), 500


@weeklyschedule_bp.route("", methods=["GET"])
@validate_querystring(WeeklyScheduleQuery)
async def get_weeklyschedules():
    """Get all weekly schedules."""
    entity_service, cyoda_auth_service = get_services()

    args = WeeklyScheduleQuery(**request.args)

    try:
        # Get all weekly schedules
        schedules = await entity_service.find_all("weeklyschedule", ENTITY_VERSION)

        # Apply state filter
        if args.state:
            schedules = [s for s in schedules if s.state == args.state]

        # Apply pagination
        total_elements = len(schedules)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_schedules = schedules[start_idx:end_idx]

        # Format response
        content = []
        for schedule in paginated_schedules:
            content.append(
                {
                    "id": schedule.technical_id,
                    "weekStartDate": schedule.data.get("weekStartDate"),
                    "weekEndDate": schedule.data.get("weekEndDate"),
                    "subscriberCount": schedule.data.get("subscriberCount"),
                    "state": schedule.state,
                }
            )

        result = {
            "content": content,
            "totalElements": total_elements,
            "totalPages": (total_elements + args.size - 1) // args.size,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get weekly schedules: {e}")
        return jsonify({"error": "Failed to get weekly schedules"}), 500
