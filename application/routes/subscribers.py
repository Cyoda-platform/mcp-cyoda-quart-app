"""
Subscriber Routes for Cat Facts Subscription System

Manages all Subscriber-related API endpoints including CRUD operations
and subscription management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


subscribers_bp = Blueprint("subscribers", __name__, url_prefix="/api/subscribers")


@subscribers_bp.route("", methods=["POST"])
@tag(["subscribers"])
@operation_id("create_subscriber")
async def create_subscriber() -> ResponseReturnValue:
    """Create a new subscriber"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Create Subscriber instance for validation
        subscriber = Subscriber(**data)
        entity_data = subscriber.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Created Subscriber with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Subscriber: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Subscriber: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>", methods=["GET"])
@tag(["subscribers"])
@operation_id("get_subscriber")
async def get_subscriber(entity_id: str) -> ResponseReturnValue:
    """Get subscriber by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Subscriber not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("", methods=["GET"])
@tag(["subscribers"])
@operation_id("list_subscribers")
async def list_subscribers() -> ResponseReturnValue:
    """List all subscribers with optional filtering"""
    try:
        # Get query parameters
        subscription_status = request.args.get("subscription_status")
        preferred_frequency = request.args.get("preferred_frequency")
        is_active = request.args.get("is_active")

        service = get_entity_service()

        # Build search conditions if filters provided
        if subscription_status or preferred_frequency or is_active:
            builder = SearchConditionRequest.builder()

            if subscription_status:
                builder.equals("subscription_status", subscription_status)
            if preferred_frequency:
                builder.equals("preferred_frequency", preferred_frequency)
            if is_active:
                builder.equals("is_active", is_active.lower() == "true")

            condition = builder.build()
            entities = await service.search(
                entity_class=Subscriber.ENTITY_NAME,
                condition=condition,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"subscribers": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Subscribers: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>", methods=["PUT"])
@tag(["subscribers"])
@operation_id("update_subscriber")
async def update_subscriber(entity_id: str) -> ResponseReturnValue:
    """Update subscriber and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Create Subscriber instance for validation
        subscriber = Subscriber(**data)
        entity_data = subscriber.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            transition=transition,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Updated Subscriber %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["subscribers"])
@operation_id("delete_subscriber")
async def delete_subscriber(entity_id: str) -> ResponseReturnValue:
    """Delete subscriber"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Deleted Subscriber %s", entity_id)
        return {
            "success": True,
            "message": "Subscriber deleted successfully",
            "entity_id": entity_id,
        }, 200

    except Exception as e:
        logger.exception("Error deleting Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>/confirm", methods=["POST"])
@tag(["subscribers"])
@operation_id("confirm_subscriber")
async def confirm_subscriber(entity_id: str) -> ResponseReturnValue:
    """Confirm subscriber subscription"""
    try:
        service = get_entity_service()

        # Execute confirm transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="confirm",
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Confirmed subscription for Subscriber %s", entity_id)
        return {
            "success": True,
            "message": "Subscription confirmed successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error confirming Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>/unsubscribe", methods=["POST"])
@tag(["subscribers"])
@operation_id("unsubscribe_subscriber")
async def unsubscribe_subscriber(entity_id: str) -> ResponseReturnValue:
    """Unsubscribe subscriber"""
    try:
        service = get_entity_service()

        # Execute unsubscribe transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="unsubscribe",
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Unsubscribed Subscriber %s", entity_id)
        return {
            "success": True,
            "message": "Unsubscribed successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error unsubscribing Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/stats", methods=["GET"])
@tag(["subscribers"])
@operation_id("get_subscriber_stats")
async def get_subscriber_stats() -> ResponseReturnValue:
    """Get subscriber statistics"""
    try:
        service = get_entity_service()

        # Get all subscribers
        subscribers = await service.find_all(
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        # Calculate statistics
        stats: Dict[str, Any] = {
            "total_subscribers": len(subscribers),
            "by_status": {},
            "by_frequency": {},
            "engagement": {
                "total_emails_sent": 0,
                "total_emails_opened": 0,
                "total_emails_clicked": 0,
                "average_engagement_rate": 0.0,
            },
        }

        total_engagement = 0.0
        active_subscribers = 0

        for subscriber_response in subscribers:
            from common.entity.entity_casting import cast_entity

            subscriber = cast_entity(subscriber_response.data, Subscriber)

            # Count by status
            status = subscriber.subscription_status
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by frequency
            freq = subscriber.preferred_frequency
            stats["by_frequency"][freq] = stats["by_frequency"].get(freq, 0) + 1

            # Aggregate engagement metrics
            stats["engagement"]["total_emails_sent"] += subscriber.total_emails_sent
            stats["engagement"]["total_emails_opened"] += subscriber.total_emails_opened
            stats["engagement"][
                "total_emails_clicked"
            ] += subscriber.total_emails_clicked

            if subscriber.is_active_subscriber():
                total_engagement += subscriber.get_engagement_rate()
                active_subscribers += 1

        # Calculate average engagement rate
        if active_subscribers > 0:
            stats["engagement"]["average_engagement_rate"] = (
                total_engagement / active_subscribers
            )

        return stats, 200

    except Exception as e:
        logger.exception("Error getting subscriber stats: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
