"""
CatFact Routes for Cyoda Client Application

Manages all CatFact-related API endpoints including CRUD operations
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

catfact_routes_bp = Blueprint("catfacts", __name__, url_prefix="/api/catfacts")


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


# ---- Request/Query Models ---------------------------------------------------


class CatFactCreateRequest(BaseModel):
    """Request model for creating a CatFact"""

    fact_text: str = Field(..., alias="factText", description="The cat fact content")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@catfact_routes_bp.route("", methods=["POST"])
@validate_request(CatFactCreateRequest)
async def create_catfact(data: CatFactCreateRequest) -> ResponseReturnValue:
    """Create a new cat fact (admin endpoint)."""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = {
            "factText": data.fact_text,
            "factLength": len(data.fact_text),
        }

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="CatFact", entity_version="1"
        )

        logger.info("Created CatFact with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "factText": entity_data["factText"],
                    "factLength": entity_data["factLength"],
                    "retrievedDate": response.data.get("retrievedDate"),
                    "scheduledSendDate": response.data.get("scheduledSendDate"),
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating CatFact: %s", str(e))
        return jsonify({"error": str(e)}), 500


@catfact_routes_bp.route("/retrieve", methods=["POST"])
async def retrieve_catfact() -> ResponseReturnValue:
    """Retrieve a new cat fact from external API."""
    try:
        service = get_services()

        # Create empty cat fact for retrieval processor
        entity_data: Dict[str, Any] = {"factText": "", "factLength": 0}

        # Save the entity (will be populated by retrieval processor)
        response = await service.save(
            entity=entity_data, entity_class="CatFact", entity_version="1"
        )

        # Trigger retrieval transition
        response = await service.execute_transition(
            entity_id=response.metadata.id,
            transition="transition_to_retrieved",
            entity_class="CatFact",
            entity_version="1",
        )

        logger.info("Retrieved CatFact with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "factText": response.data.get("factText"),
                    "factLength": response.data.get("factLength"),
                    "retrievedDate": response.data.get("retrievedDate"),
                    "state": response.metadata.state,
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error retrieving CatFact: %s", str(e))
        return jsonify({"error": str(e)}), 500


@catfact_routes_bp.route("/<entity_id>/schedule", methods=["PUT"])
@validate_request(TransitionRequest)
async def schedule_catfact(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Schedule a cat fact for weekly distribution."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_scheduled",
            entity_class="CatFact",
            entity_version="1",
        )

        logger.info("Scheduled CatFact %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "factText": response.data.get("factText"),
                    "scheduledSendDate": response.data.get("scheduledSendDate"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error scheduling CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@catfact_routes_bp.route("/<entity_id>/archive", methods=["PUT"])
@validate_request(TransitionRequest)
async def archive_catfact(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Archive a cat fact after distribution."""
    try:
        service = get_services()

        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_archived",
            entity_class="CatFact",
            entity_version="1",
        )

        logger.info("Archived CatFact %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "factText": response.data.get("factText"),
                    "state": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error archiving CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@catfact_routes_bp.route("", methods=["GET"])
async def list_catfacts() -> ResponseReturnValue:
    """Get all cat facts (admin endpoint)."""
    try:
        service = get_services()

        entities = await service.find_all(entity_class="CatFact", entity_version="1")

        # Convert to API response format
        catfacts: List[Dict[str, Any]] = []

        for entity in entities:
            catfact_data = {
                "id": entity.get_id(),
                "factText": entity.data.get("factText"),
                "factLength": entity.data.get("factLength"),
                "retrievedDate": entity.data.get("retrievedDate"),
                "scheduledSendDate": entity.data.get("scheduledSendDate"),
                "externalFactId": entity.data.get("externalFactId"),
                "state": entity.get_state(),
            }
            catfacts.append(catfact_data)

        return jsonify({"catfacts": catfacts, "totalCount": len(catfacts)}), 200

    except Exception as e:
        logger.exception("Error listing CatFacts: %s", str(e))
        return jsonify({"error": str(e)}), 500


@catfact_routes_bp.route("/<entity_id>", methods=["GET"])
async def get_catfact(entity_id: str) -> ResponseReturnValue:
    """Get cat fact by ID."""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="CatFact", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Cat fact not found"}), 404

        # Convert to API response format
        catfact_data: Dict[str, Any] = {
            "id": response.metadata.id,
            "factText": response.data.get("factText"),
            "factLength": response.data.get("factLength"),
            "retrievedDate": response.data.get("retrievedDate"),
            "scheduledSendDate": response.data.get("scheduledSendDate"),
            "externalFactId": response.data.get("externalFactId"),
            "state": response.metadata.state,
        }

        return jsonify(catfact_data), 200

    except Exception as e:
        logger.exception("Error getting CatFact %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
