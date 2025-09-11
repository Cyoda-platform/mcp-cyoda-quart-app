"""
EmailDelivery Routes for Cyoda Client Application

Manages all EmailDelivery-related API endpoints.
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

emaildelivery_routes_bp = Blueprint(
    "emaildeliveries", __name__, url_prefix="/api/emaildeliveries"
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


class EmailDeliveryCreateRequest(BaseModel):
    """Request model for creating an EmailDelivery"""

    subscriber_id: str = Field(..., alias="subscriberId", description="Subscriber ID")
    cat_fact_id: str = Field(..., alias="catFactId", description="Cat fact ID")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@emaildelivery_routes_bp.route("", methods=["POST"])
@validate_request(EmailDeliveryCreateRequest)
async def create_emaildelivery(data: EmailDeliveryCreateRequest) -> ResponseReturnValue:
    """Create a new email delivery record."""
    try:
        service = get_services()

        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data, entity_class="EmailDelivery", entity_version="1"
        )

        logger.info("Created EmailDelivery with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "subscriberId": entity_data["subscriberId"],
                    "catFactId": entity_data["catFactId"],
                    "deliveryAttempts": 0,
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating EmailDelivery: %s", str(e))
        return jsonify({"error": str(e)}), 500


@emaildelivery_routes_bp.route("/<entity_id>/send", methods=["PUT"])
@validate_request(TransitionRequest)
async def send_email(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Send email delivery."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_sent",
            entity_class="EmailDelivery",
            entity_version="1",
        )

        logger.info("Sent EmailDelivery %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "sentDate": response.data.get("sentDate"),
                    "deliveryAttempts": response.data.get("deliveryAttempts"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error sending EmailDelivery %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@emaildelivery_routes_bp.route("/<entity_id>/retry", methods=["PUT"])
@validate_request(TransitionRequest)
async def retry_email(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Retry failed email delivery."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_pending",
            entity_class="EmailDelivery",
            entity_version="1",
        )

        logger.info("Retrying EmailDelivery %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "deliveryAttempts": response.data.get("deliveryAttempts"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error retrying EmailDelivery %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@emaildelivery_routes_bp.route("", methods=["GET"])
async def list_emaildeliveries() -> ResponseReturnValue:
    """Get all email deliveries (admin endpoint)."""
    try:
        service = get_services()

        entities = await service.find_all(
            entity_class="EmailDelivery", entity_version="1"
        )

        emaildeliveries: List[Dict[str, Any]] = []

        for entity in entities:
            emaildelivery_data = {
                "id": entity.get_id(),
                "subscriberId": entity.data.get("subscriberId"),
                "catFactId": entity.data.get("catFactId"),
                "sentDate": entity.data.get("sentDate"),
                "deliveryAttempts": entity.data.get("deliveryAttempts"),
                "lastAttemptDate": entity.data.get("lastAttemptDate"),
                "errorMessage": entity.data.get("errorMessage"),
                "state": entity.get_state(),
            }
            emaildeliveries.append(emaildelivery_data)

        return (
            jsonify(
                {"emaildeliveries": emaildeliveries, "totalCount": len(emaildeliveries)}
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing EmailDeliveries: %s", str(e))
        return jsonify({"error": str(e)}), 500


@emaildelivery_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_emaildelivery(entity_id: str) -> ResponseReturnValue:
    """Get email delivery by ID."""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="EmailDelivery", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Email delivery not found"}), 404

        emaildelivery_data: Dict[str, Any] = {
            "id": response.metadata.id,
            "subscriberId": response.data.get("subscriberId"),
            "catFactId": response.data.get("catFactId"),
            "sentDate": response.data.get("sentDate"),
            "deliveryAttempts": response.data.get("deliveryAttempts"),
            "lastAttemptDate": response.data.get("lastAttemptDate"),
            "errorMessage": response.data.get("errorMessage"),
            "state": response.metadata.state,
        }

        return jsonify(emaildelivery_data), 200

    except Exception as e:
        logger.exception("Error getting EmailDelivery %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
