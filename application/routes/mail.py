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

from common.service.entity_service import SearchConditionRequest
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


# ---- Request/Query Models ---------------------------------------------------


class MailQueryParams(BaseModel):
    """Query parameters for Mail listing"""

    is_happy: Optional[bool] = Field(
        default=None, alias="isHappy", description="Filter by happiness status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results")
    offset: int = Field(default=0, description="Pagination offset")


class MailCreateRequest(BaseModel):
    """Request model for creating a Mail"""

    is_happy: bool = Field(
        ...,
        alias="isHappy",
        description="Indicates whether the mail content is happy or gloomy",
    )
    mail_list: List[str] = Field(
        ..., alias="mailList", description="List of email addresses to send the mail to"
    )


class MailUpdateRequest(BaseModel):
    """Request model for updating a Mail"""

    is_happy: Optional[bool] = Field(
        default=None,
        alias="isHappy",
        description="Indicates whether the mail content is happy or gloomy",
    )
    mail_list: Optional[List[str]] = Field(
        default=None,
        alias="mailList",
        description="List of email addresses to send the mail to",
    )
    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@mail_bp.route("", methods=["POST"])
@validate_request(MailCreateRequest)
async def create_mail(data: MailCreateRequest) -> ResponseReturnValue:
    """Create a new Mail entity"""
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
        result_data = dict(response.data)
        result_data["id"] = response.metadata.id
        result_data["state"] = response.metadata.state

        return jsonify(result_data), 201

    except Exception as e:  # pragma: no cover - keep robust error handling
        logger.exception("Error creating Mail: %s", str(e))
        return jsonify({"error": str(e)}), 500


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
    """List Mails with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.is_happy is not None:
            search_conditions["isHappy"] = str(query_args.is_happy).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class="Mail",
                condition=condition,
                entity_version="1",
            )
        else:
            entities = await service.find_all(entity_class="Mail", entity_version="1")

        # Convert to API response format
        entity_list: List[Dict[str, Any]] = []
        for entity in entities:
            entity_data = {
                "id": entity.get_id(),
                "isHappy": entity.data.get("isHappy"),
                "mailList": entity.data.get("mailList"),
                "state": entity.get_state(),
            }
            entity_list.append(entity_data)

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify(paginated_entities), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing Mails: %s", str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(MailUpdateRequest)
async def update_mail(entity_id: str, data: MailUpdateRequest) -> ResponseReturnValue:
    """Update Mail and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body or query parameter
        transition: Optional[str] = data.transition or request.args.get(
            "transitionName"
        )

        # Convert request to entity data (exclude None values)
        entity_data: Dict[str, Any] = {
            k: v
            for k, v in data.model_dump(by_alias=True, exclude_none=True).items()
            if k != "transition"
        }

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class="Mail",
            transition=transition,
            entity_version="1",
        )

        logger.info("Updated Mail %s", entity_id)

        # Convert to API response format
        result_data: Dict[str, Any] = dict(response.data)
        result_data["id"] = response.metadata.id
        result_data["state"] = response.metadata.state

        return jsonify(result_data), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error updating Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_mail(entity_id: str) -> ResponseReturnValue:
    """Delete Mail"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        logger.info("Deleted Mail %s", entity_id)

        return "", 204

    except Exception as e:  # pragma: no cover
        logger.exception("Error deleting Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mail_bp.route("/<entity_id>/retry", methods=["POST"])
async def retry_mail(entity_id: str) -> ResponseReturnValue:
    """Retry failed mail delivery (manual transition from FAILED to PENDING)"""
    try:
        service = get_services()

        # Get transition name from query parameter
        transition_name = request.args.get(
            "transitionName", "transition_to_pending_retry"
        )

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=transition_name,
            entity_class="Mail",
            entity_version="1",
        )

        logger.info("Executed retry transition on Mail %s", entity_id)

        # Convert to API response format
        result_data: Dict[str, Any] = dict(response.data)
        result_data["id"] = response.metadata.id
        result_data["state"] = response.metadata.state

        return jsonify(result_data), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error retrying Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
