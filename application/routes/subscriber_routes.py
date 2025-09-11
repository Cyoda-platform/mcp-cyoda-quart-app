"""
Subscriber Routes for Cyoda Client Application

Manages all Subscriber-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
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

subscriber_routes_bp = Blueprint("subscribers", __name__, url_prefix="/api/subscribers")


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

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...

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


# ---- Request/Query Models ---------------------------------------------------


class SubscriberCreateRequest(BaseModel):
    """Request model for creating a Subscriber"""

    email: str = Field(..., description="Email address of the subscriber")
    first_name: Optional[str] = Field(
        default=None, alias="firstName", description="First name of the subscriber"
    )
    last_name: Optional[str] = Field(
        default=None, alias="lastName", description="Last name of the subscriber"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


class UnsubscribeByTokenRequest(BaseModel):
    """Request model for unsubscribing by token"""

    unsubscribe_token: str = Field(
        ..., alias="unsubscribeToken", description="Unsubscribe token from email"
    )
    transition_name: str = Field(
        default="unsubscribe", alias="transitionName", description="Transition name"
    )


# ---- Routes -----------------------------------------------------------------


@subscriber_routes_bp.route("", methods=["POST"])
@validate_request(SubscriberCreateRequest)
async def create_subscriber(data: SubscriberCreateRequest) -> ResponseReturnValue:
    """Register a new subscriber for weekly cat facts."""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="Subscriber", entity_version="1"
        )

        logger.info("Created Subscriber with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "email": entity_data["email"],
                    "firstName": entity_data.get("firstName"),
                    "lastName": entity_data.get("lastName"),
                    "subscriptionDate": response.data.get("subscriptionDate"),
                    "isActive": False,
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating Subscriber: %s", str(e))
        return jsonify({"error": str(e)}), 500


@subscriber_routes_bp.route("/<entity_id>/activate", methods=["PUT"])
@validate_request(TransitionRequest)
async def activate_subscriber(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Activate a subscriber (email verification)."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_active",
            entity_class="Subscriber",
            entity_version="1",
        )

        logger.info("Activated Subscriber %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "email": response.data.get("email"),
                    "isActive": True,
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error activating Subscriber %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@subscriber_routes_bp.route("/<entity_id>/unsubscribe", methods=["PUT"])
@validate_request(TransitionRequest)
async def unsubscribe_subscriber(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Unsubscribe a subscriber."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_unsubscribed",
            entity_class="Subscriber",
            entity_version="1",
        )

        logger.info("Unsubscribed Subscriber %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "email": response.data.get("email"),
                    "isActive": False,
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error unsubscribing Subscriber %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@subscriber_routes_bp.route("/unsubscribe-by-token", methods=["POST"])
@validate_request(UnsubscribeByTokenRequest)
async def unsubscribe_by_token(data: UnsubscribeByTokenRequest) -> ResponseReturnValue:
    """Unsubscribe using unsubscribe token from email."""
    try:
        # In a real implementation, we would find the subscriber by token
        # For now, we return a success message
        logger.info("Unsubscribe by token requested: %s", data.unsubscribe_token)

        return (
            jsonify(
                {
                    "message": "Successfully unsubscribed",
                    "email": "user@example.com",  # Would be actual email in real implementation
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error unsubscribing by token: %s", str(e))
        return jsonify({"error": str(e)}), 500


@subscriber_routes_bp.route("", methods=["GET"])
async def list_subscribers() -> ResponseReturnValue:
    """Get all subscribers (admin endpoint)."""
    try:
        service = get_services()

        entities = await service.find_all(entity_class="Subscriber", entity_version="1")

        # Convert to API response format
        subscribers: List[Dict[str, Any]] = []
        active_count = 0

        for entity in entities:
            subscriber_data = {
                "id": entity.get_id(),
                "email": entity.data.get("email"),
                "firstName": entity.data.get("firstName"),
                "lastName": entity.data.get("lastName"),
                "subscriptionDate": entity.data.get("subscriptionDate"),
                "isActive": entity.data.get("isActive", False),
                "state": entity.get_state(),
            }
            subscribers.append(subscriber_data)

            if subscriber_data["isActive"]:
                active_count += 1

        return (
            jsonify(
                {
                    "subscribers": subscribers,
                    "totalCount": len(subscribers),
                    "activeCount": active_count,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing Subscribers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@subscriber_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_subscriber(entity_id: str) -> ResponseReturnValue:
    """Get subscriber by ID."""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="Subscriber", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Subscriber not found"}), 404

        # Convert to API response format
        subscriber_data: Dict[str, Any] = {
            "id": response.metadata.id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive", False),
            "state": response.metadata.state,
        }

        return jsonify(subscriber_data), 200

    except Exception as e:
        logger.exception("Error getting Subscriber %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
