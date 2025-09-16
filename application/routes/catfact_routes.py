"""
CatFact routes for the cat fact subscription system.
"""

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from quart import Blueprint, abort, jsonify, request
from quart_schema import validate_json, validate_querystring

from common.config.config import ENTITY_VERSION
from service.services import get_auth_service, get_entity_service

logger = logging.getLogger(__name__)

catfact_bp = Blueprint("catfacts", __name__, url_prefix="/api/catfacts")


class CatFactCreateRequest(BaseModel):
    """Request model for creating a cat fact."""

    pass  # Empty body for manual trigger


class CatFactScheduleRequest(BaseModel):
    """Request model for scheduling a cat fact."""

    scheduledSendDate: datetime
    transitionName: str


class CatFactTransitionRequest(BaseModel):
    """Request model for cat fact transitions."""

    transitionName: str


class CatFactQuery(BaseModel):
    """Query parameters for listing cat facts."""

    state: Optional[str] = None
    page: int = 0
    size: int = 20


def get_services():
    """Get services from the registry lazily."""
    return get_entity_service(), get_auth_service()


@catfact_bp.route("", methods=["POST"])
@validate_json(CatFactCreateRequest)
async def create_catfact():
    """Manually trigger cat fact retrieval."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Create empty cat fact entity (triggers initial → retrieved transition automatically)
        catfact_data = {"fact": ""}  # Will be populated by CatFactRetrievalProcessor

        response = await entity_service.save(catfact_data, "catfact", ENTITY_VERSION)

        result = {
            "id": response.technical_id,
            "fact": response.data.get("fact"),
            "length": response.data.get("length"),
            "retrievedDate": response.data.get("retrievedDate"),
            "state": response.state,
        }

        return jsonify(result), 201

    except Exception as e:
        logger.exception(f"Failed to create cat fact: {e}")
        return jsonify({"error": "Failed to create cat fact"}), 500


@catfact_bp.route("/<catfact_id>", methods=["GET"])
async def get_catfact(catfact_id: str):
    """Get cat fact details by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        response = await entity_service.get_by_id(catfact_id, "catfact", ENTITY_VERSION)

        result = {
            "id": response.technical_id,
            "fact": response.data.get("fact"),
            "length": response.data.get("length"),
            "retrievedDate": response.data.get("retrievedDate"),
            "scheduledSendDate": response.data.get("scheduledSendDate"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get cat fact {catfact_id}: {e}")
        abort(404)


@catfact_bp.route("/<catfact_id>/schedule", methods=["PUT"])
@validate_json(CatFactScheduleRequest)
async def schedule_catfact(catfact_id: str):
    """Schedule cat fact for distribution."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current cat fact
        current_response = await entity_service.get_by_id(
            catfact_id, "catfact", ENTITY_VERSION
        )

        # Update with scheduled send date
        updated_data = current_response.data.copy()
        updated_data["scheduledSendDate"] = data["scheduledSendDate"].isoformat()

        response = await entity_service.update(
            catfact_id,
            updated_data,
            "catfact",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION,
        )

        result = {
            "id": response.technical_id,
            "fact": response.data.get("fact"),
            "scheduledSendDate": response.data.get("scheduledSendDate"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to schedule cat fact {catfact_id}: {e}")
        return jsonify({"error": "Failed to schedule cat fact"}), 500


@catfact_bp.route("/<catfact_id>/distribute", methods=["PUT"])
@validate_json(CatFactTransitionRequest)
async def distribute_catfact(catfact_id: str):
    """Distribute cat fact to subscribers."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current cat fact
        current_response = await entity_service.get_by_id(
            catfact_id, "catfact", ENTITY_VERSION
        )

        # Update with distribution transition
        response = await entity_service.update(
            catfact_id,
            current_response.data,
            "catfact",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION,
        )

        # Get distribution count from metadata
        distribution_count = response.data.get("metadata", {}).get(
            "distribution_count", 0
        )

        result = {
            "id": response.technical_id,
            "fact": response.data.get("fact"),
            "state": response.state,
            "distributionCount": distribution_count,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to distribute cat fact {catfact_id}: {e}")
        return jsonify({"error": "Failed to distribute cat fact"}), 500


@catfact_bp.route("", methods=["GET"])
@validate_querystring(CatFactQuery)
async def get_catfacts():
    """Get all cat facts with optional filtering."""
    entity_service, cyoda_auth_service = get_services()

    args = CatFactQuery(**request.args)

    try:
        # Get all cat facts
        catfacts = await entity_service.find_all("catfact", ENTITY_VERSION)

        # Apply state filter
        if args.state:
            catfacts = [cf for cf in catfacts if cf.state == args.state]

        # Apply pagination
        total_elements = len(catfacts)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_catfacts = catfacts[start_idx:end_idx]

        # Format response
        content = []
        for catfact in paginated_catfacts:
            content.append(
                {
                    "id": catfact.technical_id,
                    "fact": catfact.data.get("fact"),
                    "length": catfact.data.get("length"),
                    "retrievedDate": catfact.data.get("retrievedDate"),
                    "state": catfact.state,
                }
            )

        result = {
            "content": content,
            "totalElements": total_elements,
            "totalPages": (total_elements + args.size - 1) // args.size,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get cat facts: {e}")
        return jsonify({"error": "Failed to get cat facts"}), 500
