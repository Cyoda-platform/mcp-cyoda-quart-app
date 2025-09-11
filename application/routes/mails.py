"""
Mail Routes for Cyoda Client Application

Manages all Mail-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import validate_querystring, validate_request

from common.service.entity_service import (
    SearchConditionRequest,
    SearchConditionRequestBuilder,
)

logger = logging.getLogger(__name__)

# Blueprint for mail routes
mails_bp = Blueprint("mails", __name__, url_prefix="/api/mails")


# ---- Service Protocol -------------------------------------------------------


class _SavedEntity(Protocol):
    @property
    def data(self) -> Dict[str, Any]: ...
    @property
    def metadata(self) -> Any: ...


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...
    @property
    def data(self) -> Dict[str, Any]: ...
    @property
    def metadata(self) -> Any: ...


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

    async def delete(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> bool: ...


def get_services() -> EntityServiceProtocol:
    """Get entity service instance"""
    from services.services import get_entity_service

    return cast(EntityServiceProtocol, get_entity_service())


# ---- Request/Query Models ---------------------------------------------------


class MailQueryParams(BaseModel):
    """Query parameters for Mail listing"""

    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    isHappy: Optional[bool] = Field(
        default=None, description="Filter by happy/gloomy type"
    )
    limit: int = Field(default=50, description="Number of results")
    offset: int = Field(default=0, description="Pagination offset")


class MailCreateRequest(BaseModel):
    """Request model for creating a Mail"""

    isHappy: bool = Field(
        ...,
        description="Indicates whether the mail content is happy (true) or gloomy (false)",
    )
    mailList: List[str] = Field(
        ..., description="List of email addresses to send the mail to"
    )


class MailUpdateRequest(BaseModel):
    """Request model for updating a Mail"""

    isHappy: Optional[bool] = Field(
        default=None,
        description="Indicates whether the mail content is happy (true) or gloomy (false)",
    )
    mailList: Optional[List[str]] = Field(
        default=None, description="List of email addresses to send the mail to"
    )
    transitionName: Optional[str] = Field(
        default=None, description="Workflow transition to trigger"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transitionName: str = Field(..., description="Name of the transition to execute")


# ---- Routes -----------------------------------------------------------------


@mails_bp.route("", methods=["POST"])
@validate_request(MailCreateRequest)
async def create_mail(
    data: MailCreateRequest,
) -> ResponseReturnValue:
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

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "isHappy": response.data.get("isHappy"),
                    "mailList": response.data.get("mailList"),
                    "state": response.metadata.state,
                    "createdAt": response.metadata.created_at,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating Mail: %s", str(e))
        return jsonify({"error": str(e)}), 500


@mails_bp.route("/<entity_id>", methods=["GET"])
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
        entity_data["createdAt"] = response.metadata.created_at
        entity_data["updatedAt"] = response.metadata.updated_at

        return jsonify(entity_data), 200

    except Exception as e:
        logger.exception("Error getting Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mails_bp.route("", methods=["GET"])
@validate_querystring(MailQueryParams)
async def list_mails(
    query_args: MailQueryParams,
) -> ResponseReturnValue:
    """List Mails with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        builder = SearchConditionRequestBuilder()

        if query_args.state:
            builder.equals("state", query_args.state)

        if query_args.isHappy is not None:
            builder.equals("isHappy", query_args.isHappy)

        search_request = builder.build()
        results = await service.search(
            entity_class="Mail", condition=search_request, entity_version="1"
        )

        # Convert to simple format for API response
        mails = [
            {
                "id": r.get_id(),
                "isHappy": r.data.get("isHappy"),
                "state": r.metadata.state,
            }
            for r in results
        ]

        return jsonify({"mails": mails, "total": len(mails)}), 200

    except Exception as e:
        logger.exception("Error listing Mails: %s", str(e))
        return jsonify({"error": str(e)}), 500


@mails_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(MailUpdateRequest)
async def update_mail(entity_id: str, data: MailUpdateRequest) -> ResponseReturnValue:
    """Update Mail and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body
        transition: Optional[str] = data.transitionName

        # Convert request to entity data (exclude None values)
        entity_data: Dict[str, Any] = {
            k: v
            for k, v in data.model_dump(by_alias=True, exclude_none=True).items()
            if k != "transitionName"
        }

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class="Mail",
            transition=transition,
            entity_version="1",
        )

        logger.info("Updated Mail with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "isHappy": response.data.get("isHappy"),
                    "mailList": response.data.get("mailList"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error updating Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mails_bp.route("/<entity_id>/resend", methods=["PUT"])
@validate_request(TransitionRequest)
async def resend_mail(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Trigger resending of mail (from HAPPY_SENT or GLOOMY_SENT back to PENDING)"""
    try:
        service = get_services()

        # Get current entity to check state
        current_entity = await service.get_by_id(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        if not current_entity:
            return jsonify({"error": "Mail not found"}), 404

        # Validate transition name
        valid_transitions = ["transition_to_pending_resend"]
        if data.transitionName not in valid_transitions:
            return jsonify({"error": f"Invalid transition: {data.transitionName}"}), 400

        # Execute the transition (no entity data changes, just state transition)
        response = await service.update(
            entity_id=entity_id,
            entity={},  # No data changes
            entity_class="Mail",
            transition=data.transitionName,
            entity_version="1",
        )

        logger.info("Triggered resend for Mail with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "state": response.metadata.state,
                    "message": "Mail queued for resending",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error resending Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@mails_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_mail(entity_id: str) -> ResponseReturnValue:
    """Delete a Mail"""
    try:
        service = get_services()

        success = await service.delete(
            entity_id=entity_id, entity_class="Mail", entity_version="1"
        )

        if not success:
            return jsonify({"error": "Mail not found"}), 404

        logger.info("Deleted Mail with ID: %s", entity_id)

        return jsonify({"message": "Mail deleted successfully"}), 200

    except Exception as e:
        logger.exception("Error deleting Mail %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
