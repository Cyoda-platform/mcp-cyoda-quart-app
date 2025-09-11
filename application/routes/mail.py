"""
Mail Routes for Cyoda Client Application

Manages all Mail-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_querystring, validate_request

from common.service.entity_service import (
    SearchConditionRequest,
    SearchConditionRequestBuilder,
    SearchOperator,
)
from services.services import get_entity_service

# Imported for possible external references / type hints
from ..entity.mail import Mail  # noqa: F401

logger = logging.getLogger(__name__)

mail_bp = Blueprint("mail", __name__, url_prefix="/api/mail")


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

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...

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

    async def delete_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> None: ...

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
        # get_entity_service() is likely untyped, so cast to our protocol
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Request/Response Models ------------------------------------------------


class MailCreateRequest(BaseModel):
    """Request model for creating a new Mail"""

    is_happy: bool = Field(
        ..., alias="isHappy", description="Whether the mail is happy or gloomy"
    )
    mail_list: List[str] = Field(
        ..., alias="mailList", description="List of email addresses"
    )


class MailUpdateRequest(BaseModel):
    """Request model for updating a Mail"""

    is_happy: Optional[bool] = Field(
        None, alias="isHappy", description="Whether the mail is happy or gloomy"
    )
    mail_list: Optional[List[str]] = Field(
        None, alias="mailList", description="List of email addresses"
    )
    transition: Optional[str] = Field(
        None, description="Optional workflow transition to execute"
    )


class MailQueryParams(BaseModel):
    """Query parameters for listing mails"""

    state: Optional[str] = Field(None, description="Filter by mail state")
    is_happy: Optional[bool] = Field(
        None, alias="isHappy", description="Filter by happiness state"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition: str = Field(..., description="Name of the transition to execute")


# ---- Route Handlers ---------------------------------------------------------


@mail_bp.route("", methods=["POST"])
@validate_request(MailCreateRequest)
async def create_mail(data: MailCreateRequest) -> ResponseReturnValue:
    """Create a new Mail"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="Mail", entity_version="1"
        )

        logger.info("Created Mail with ID: %s", response.metadata.id)

        # Return response with entity data
        entity_data_response = dict(response.data)
        entity_data_response["id"] = response.metadata.id
        entity_data_response["state"] = response.metadata.state
        entity_data_response["createdAt"] = entity_data_response.get("created_at")

        return jsonify(entity_data_response), 201

    except Exception as e:
        logger.exception("Error creating Mail: %s", str(e))
        return jsonify({"error": str(e)}), 400


@mail_bp.route("/<entity_id>", methods=["GET"])
async def get_mail(entity_id: str) -> ResponseReturnValue:
    """Get Mail by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Mail not found"}), 404

        # Convert to API response format
        entity_data: Dict[str, Any] = dict(response.data)
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error getting Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("", methods=["GET"])
@validate_querystring(MailQueryParams)
async def list_mails(query_args: MailQueryParams) -> ResponseReturnValue:
    """List all mails with optional filtering"""
    try:
        service = get_services()

        # Build search conditions if filters are provided
        if query_args.state or query_args.is_happy is not None:
            builder = SearchConditionRequestBuilder()

            if query_args.state:
                builder.add_condition("state", SearchOperator.EQUALS, query_args.state)

            if query_args.is_happy is not None:
                builder.add_condition(
                    "isHappy", SearchOperator.EQUALS, query_args.is_happy
                )

            condition = builder.build()
            entities = await service.search("Mail", condition, "1")
        else:
            # Get all entities if no filters
            entities = await service.find_all(entity_class="Mail", entity_version="1")

        # Convert to response format
        mails = []
        for entity in entities:
            mail_data = dict(entity.data)
            mail_data["id"] = entity.get_id()
            mail_data["state"] = entity.get_state()
            mails.append(mail_data)

        return jsonify({"mails": mails, "total": len(mails)}), 200

    except Exception as e:
        logger.exception("Error listing mails: %s", str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(MailUpdateRequest)
async def update_mail(entity_id: str, data: MailUpdateRequest) -> ResponseReturnValue:
    """Update Mail and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body or query parameter
        transition: Optional[str] = data.transition or request.args.get("transition")

        # Convert request to entity data (exclude None values)
        entity_data: Dict[str, Any] = {
            k: v
            for k, v in data.model_dump(by_alias=True, exclude_none=True).items()
            if k != "transition"
        }

        if not entity_data:
            return jsonify({"error": "No data provided for update"}), 400

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class="Mail",
            transition=transition,
            entity_version="1",
        )

        logger.info("Updated Mail with ID: %s", response.metadata.id)

        # Convert to API response format
        updated_data: Dict[str, Any] = dict(response.data)
        updated_data["id"] = response.metadata.id
        updated_data["state"] = response.metadata.state

        return jsonify(updated_data), 200

    except Exception as e:
        logger.exception("Error updating Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_mail(entity_id: str) -> ResponseReturnValue:
    """Delete Mail by ID"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        logger.info("Deleted Mail with ID: %s", entity_id)
        return "", 204

    except Exception as e:
        logger.exception("Error deleting Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>/transition", methods=["POST"])
@validate_request(TransitionRequest)
async def trigger_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Execute a specific workflow transition"""
    try:
        service = get_services()

        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        if not current_entity:
            return jsonify({"error": "Mail not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition,
            entity_class="Mail",
            entity_version="1",
        )

        logger.info(
            "Executed transition '%s' on Mail %s: %s -> %s",
            data.transition,
            entity_id,
            previous_state,
            response.metadata.state,
        )

        # Convert to API response format
        entity_data: Dict[str, Any] = dict(response.data)
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:
        logger.exception(
            "Error executing transition '%s' on Mail %s: %s",
            data.transition,
            entity_id,
            str(e),
        )
        return jsonify({"error": str(e)}), 400
