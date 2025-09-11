"""
WeeklySchedule Routes for Cyoda Client Application

Manages all WeeklySchedule-related API endpoints.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import validate_request

from services.services import get_entity_service

logger = logging.getLogger(__name__)

weeklyschedule_routes_bp = Blueprint(
    "weeklyschedules", __name__, url_prefix="/api/weeklyschedules"
)


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
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def find_all(
        self, *, entity_class: str, entity_version: str
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


# ---- Request Models ---------------------------------------------------------


class WeeklyScheduleCreateRequest(BaseModel):
    """Request model for creating a WeeklySchedule"""

    week_start_date: str = Field(
        ..., alias="weekStartDate", description="Week start date (Monday)"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@weeklyschedule_routes_bp.route("", methods=["POST"])
@validate_request(WeeklyScheduleCreateRequest)
async def create_weeklyschedule(
    data: WeeklyScheduleCreateRequest,
) -> ResponseReturnValue:
    """Create a new weekly schedule."""
    try:
        service = get_services()

        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data, entity_class="WeeklySchedule", entity_version="1"
        )

        logger.info("Created WeeklySchedule with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "weekStartDate": entity_data["weekStartDate"],
                    "weekEndDate": response.data.get("weekEndDate"),
                    "scheduledSendDate": response.data.get("scheduledSendDate"),
                    "totalSubscribers": response.data.get("totalSubscribers", 0),
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating WeeklySchedule: %s", str(e))
        return jsonify({"error": str(e)}), 500


@weeklyschedule_routes_bp.route("/<entity_id>/assign-fact", methods=["PUT"])
@validate_request(TransitionRequest)
async def assign_fact(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Assign cat fact to weekly schedule."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_fact_assigned",
            entity_class="WeeklySchedule",
            entity_version="1",
        )

        logger.info("Assigned fact to WeeklySchedule %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "catFactId": response.data.get("catFactId"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error assigning fact to WeeklySchedule %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@weeklyschedule_routes_bp.route("/<entity_id>/send-emails", methods=["PUT"])
@validate_request(TransitionRequest)
async def send_emails(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Send emails for weekly schedule."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_emails_sent",
            entity_class="WeeklySchedule",
            entity_version="1",
        )

        logger.info("Sent emails for WeeklySchedule %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "emailsSent": response.data.get("emailsSent"),
                    "emailsFailed": response.data.get("emailsFailed"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error sending emails for WeeklySchedule %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@weeklyschedule_routes_bp.route("", methods=["GET"])
async def list_weeklyschedules() -> ResponseReturnValue:
    """Get all weekly schedules (admin endpoint)."""
    try:
        service = get_services()

        entities = await service.find_all(
            entity_class="WeeklySchedule", entity_version="1"
        )

        weeklyschedules: List[Dict[str, Any]] = []

        for entity in entities:
            schedule_data = {
                "id": entity.get_id(),
                "weekStartDate": entity.data.get("weekStartDate"),
                "weekEndDate": entity.data.get("weekEndDate"),
                "scheduledSendDate": entity.data.get("scheduledSendDate"),
                "catFactId": entity.data.get("catFactId"),
                "totalSubscribers": entity.data.get("totalSubscribers"),
                "emailsSent": entity.data.get("emailsSent"),
                "emailsFailed": entity.data.get("emailsFailed"),
                "state": entity.get_state(),
            }
            weeklyschedules.append(schedule_data)

        return (
            jsonify(
                {"weeklyschedules": weeklyschedules, "totalCount": len(weeklyschedules)}
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing WeeklySchedules: %s", str(e))
        return jsonify({"error": str(e)}), 500


@weeklyschedule_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_weeklyschedule(entity_id: str) -> ResponseReturnValue:
    """Get weekly schedule by ID."""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="WeeklySchedule", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Weekly schedule not found"}), 404

        schedule_data: Dict[str, Any] = {
            "id": response.metadata.id,
            "weekStartDate": response.data.get("weekStartDate"),
            "weekEndDate": response.data.get("weekEndDate"),
            "scheduledSendDate": response.data.get("scheduledSendDate"),
            "catFactId": response.data.get("catFactId"),
            "totalSubscribers": response.data.get("totalSubscribers"),
            "emailsSent": response.data.get("emailsSent"),
            "emailsFailed": response.data.get("emailsFailed"),
            "state": response.metadata.state,
        }

        return jsonify(schedule_data), 200

    except Exception as e:
        logger.exception("Error getting WeeklySchedule %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
