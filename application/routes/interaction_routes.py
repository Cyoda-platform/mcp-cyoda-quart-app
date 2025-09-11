"""
Interaction Routes for Cyoda Client Application

Manages all Interaction-related API endpoints.
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

interaction_routes_bp = Blueprint(
    "interactions", __name__, url_prefix="/api/interactions"
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


class InteractionCreateRequest(BaseModel):
    """Request model for creating an Interaction"""

    subscriber_id: str = Field(..., alias="subscriberId", description="Subscriber ID")
    email_delivery_id: Optional[str] = Field(
        default=None, alias="emailDeliveryId", description="Email delivery ID"
    )
    interaction_type: str = Field(
        ..., alias="interactionType", description="Type of interaction"
    )
    ip_address: Optional[str] = Field(
        default=None, alias="ipAddress", description="IP address"
    )
    user_agent: Optional[str] = Field(
        default=None, alias="userAgent", description="User agent"
    )
    additional_data: Optional[str] = Field(
        default=None, alias="additionalData", description="Additional data"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@interaction_routes_bp.route("", methods=["POST"])
@validate_request(InteractionCreateRequest)
async def create_interaction(data: InteractionCreateRequest) -> ResponseReturnValue:
    """Record a new user interaction."""
    try:
        service = get_services()

        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data, entity_class="Interaction", entity_version="1"
        )

        logger.info("Created Interaction with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "subscriberId": entity_data["subscriberId"],
                    "interactionType": entity_data["interactionType"],
                    "interactionDate": response.data.get("interactionDate"),
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating Interaction: %s", str(e))
        return jsonify({"error": str(e)}), 500


@interaction_routes_bp.route("/<entity_id>/process", methods=["PUT"])
@validate_request(TransitionRequest)
async def process_interaction(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Process interaction for analytics."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_processed",
            entity_class="Interaction",
            entity_version="1",
        )

        logger.info("Processed Interaction %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "interactionType": response.data.get("interactionType"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error processing Interaction %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@interaction_routes_bp.route("", methods=["GET"])
async def list_interactions() -> ResponseReturnValue:
    """Get all interactions (admin endpoint)."""
    try:
        service = get_services()

        entities = await service.find_all(
            entity_class="Interaction", entity_version="1"
        )

        interactions: List[Dict[str, Any]] = []

        for entity in entities:
            interaction_data = {
                "id": entity.get_id(),
                "subscriberId": entity.data.get("subscriberId"),
                "emailDeliveryId": entity.data.get("emailDeliveryId"),
                "interactionType": entity.data.get("interactionType"),
                "interactionDate": entity.data.get("interactionDate"),
                "ipAddress": entity.data.get("ipAddress"),
                "userAgent": entity.data.get("userAgent"),
                "state": entity.get_state(),
            }
            interactions.append(interaction_data)

        return (
            jsonify({"interactions": interactions, "totalCount": len(interactions)}),
            200,
        )

    except Exception as e:
        logger.exception("Error listing Interactions: %s", str(e))
        return jsonify({"error": str(e)}), 500


@interaction_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_interaction(entity_id: str) -> ResponseReturnValue:
    """Get interaction by ID."""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="Interaction", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Interaction not found"}), 404

        interaction_data: Dict[str, Any] = {
            "id": response.metadata.id,
            "subscriberId": response.data.get("subscriberId"),
            "emailDeliveryId": response.data.get("emailDeliveryId"),
            "interactionType": response.data.get("interactionType"),
            "interactionDate": response.data.get("interactionDate"),
            "ipAddress": response.data.get("ipAddress"),
            "userAgent": response.data.get("userAgent"),
            "additionalData": response.data.get("additionalData"),
            "state": response.metadata.state,
        }

        return jsonify(interaction_data), 200

    except Exception as e:
        logger.exception("Error getting Interaction %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
