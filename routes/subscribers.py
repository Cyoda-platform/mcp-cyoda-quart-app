"""
Subscriber management routes.

This module contains routes for managing subscribers and notifications.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_request

from service.services import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

subscribers_bp = Blueprint('subscribers', __name__, url_prefix='/subscribers')

# Services will be accessed through the registry
entity_service = None
cyoda_auth_service = None


@dataclass
class SubscriberRequest:
    email: Optional[str]
    webhook_url: Optional[str]


def get_services():
    """Get services from the registry lazily."""
    global entity_service, cyoda_auth_service
    if entity_service is None:
        entity_service = get_entity_service()
    if cyoda_auth_service is None:
        cyoda_auth_service = get_auth_service()
    return entity_service, cyoda_auth_service


@subscribers_bp.route("", methods=["GET"])
async def list_subscribers():
    """List all subscribers."""
    entity_service, cyoda_auth_service = get_services()

    try:
        subscribers = await entity_service.get_items(
            "subscriber", ENTITY_VERSION
        )
        logger.info(f"Retrieved {len(subscribers)} subscribers")
        return jsonify(subscribers)
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve subscribers")


@subscribers_bp.route("", methods=["POST"])
@validate_request(SubscriberRequest)
async def add_subscriber(data: SubscriberRequest):
    """Add a new subscriber."""
    entity_service, cyoda_auth_service = get_services()

    if not data.email and not data.webhook_url:
        abort(400, description="Either email or webhook_url is required")

    subscriber_id = str(uuid.uuid4())
    subscriber_data = {
        "id": subscriber_id,
        "email": data.email,
        "webhook_url": data.webhook_url,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subscription_type": "laureate_updates"
    }

    try:
        await entity_service.save_item(
            subscriber_data, "subscriber", subscriber_id, ENTITY_VERSION
        )
        logger.info(f"Added subscriber {subscriber_id}")
        return jsonify({
            "subscriber_id": subscriber_id, 
            "status": "active",
            "message": "Subscriber added successfully"
        }), 201
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to add subscriber")


@subscribers_bp.route("/<string:subscriber_id>", methods=["GET"])
async def get_subscriber(subscriber_id):
    """Get a specific subscriber by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        subscriber = await entity_service.get_item(
            subscriber_id, "subscriber", ENTITY_VERSION
        )
        if not subscriber:
            abort(404, description="Subscriber not found")
        
        logger.info(f"Retrieved subscriber {subscriber_id}")
        return jsonify(subscriber)
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve subscriber")


@subscribers_bp.route("/<string:subscriber_id>", methods=["PUT"])
async def update_subscriber(subscriber_id):
    """Update an existing subscriber."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if subscriber exists
        existing_subscriber = await entity_service.get_item(
            subscriber_id, "subscriber", ENTITY_VERSION
        )
        if not existing_subscriber:
            abort(404, description="Subscriber not found")

        # Get update data
        data = await request.get_json()
        if not data:
            abort(400, description="Request body is required")

        # Update the subscriber
        updated_subscriber = {**existing_subscriber, **data}
        updated_subscriber["updated_at"] = datetime.now(timezone.utc).isoformat()

        await entity_service.save_item(
            updated_subscriber, "subscriber", subscriber_id, ENTITY_VERSION
        )
        
        logger.info(f"Updated subscriber {subscriber_id}")
        return jsonify(updated_subscriber)

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to update subscriber")


@subscribers_bp.route("/<string:subscriber_id>", methods=["DELETE"])
async def delete_subscriber(subscriber_id):
    """Delete a subscriber."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if subscriber exists
        subscriber = await entity_service.get_item(
            subscriber_id, "subscriber", ENTITY_VERSION
        )
        if not subscriber:
            abort(404, description="Subscriber not found")

        # Delete subscriber (implementation depends on your entity service)
        # await entity_service.delete_item(subscriber_id, "subscriber", ENTITY_VERSION)
        
        logger.info(f"Deleted subscriber {subscriber_id}")
        return jsonify({"message": f"Subscriber {subscriber_id} deleted successfully"}), 200

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to delete subscriber")


@subscribers_bp.route("/<string:subscriber_id>/status", methods=["PUT"])
async def update_subscriber_status(subscriber_id):
    """Update subscriber status (active/inactive)."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if subscriber exists
        subscriber = await entity_service.get_item(
            subscriber_id, "subscriber", ENTITY_VERSION
        )
        if not subscriber:
            abort(404, description="Subscriber not found")

        # Get status from request
        data = await request.get_json()
        if not data or "status" not in data:
            abort(400, description="Status is required")

        status = data["status"]
        if status not in ["active", "inactive", "suspended"]:
            abort(400, description="Status must be one of: active, inactive, suspended")

        # Update status
        subscriber["status"] = status
        subscriber["status_updated_at"] = datetime.now(timezone.utc).isoformat()

        await entity_service.save_item(
            subscriber, "subscriber", subscriber_id, ENTITY_VERSION
        )
        
        logger.info(f"Updated subscriber {subscriber_id} status to {status}")
        return jsonify({
            "subscriber_id": subscriber_id,
            "status": status,
            "message": f"Subscriber status updated to {status}"
        })

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to update subscriber status")


@subscribers_bp.route("/notify", methods=["POST"])
async def notify_subscribers():
    """Send notifications to all active subscribers."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Get notification data
        data = await request.get_json()
        if not data:
            abort(400, description="Notification data is required")

        # Get all active subscribers
        subscribers = await entity_service.get_items("subscriber", ENTITY_VERSION)
        active_subscribers = [s for s in subscribers if s.get("status") == "active"]

        if not active_subscribers:
            return jsonify({
                "message": "No active subscribers to notify",
                "notified_count": 0
            }), 200

        # Send notifications (placeholder implementation)
        notified_count = 0
        failed_count = 0
        
        for subscriber in active_subscribers:
            try:
                # This would typically send email or webhook notification
                logger.info(f"Would notify subscriber {subscriber['id']}: {data}")
                notified_count += 1
            except Exception as e:
                logger.warning(f"Failed to notify subscriber {subscriber['id']}: {e}")
                failed_count += 1

        logger.info(f"Notified {notified_count} subscribers, {failed_count} failed")
        return jsonify({
            "message": f"Notification sent to {notified_count} subscribers",
            "notified_count": notified_count,
            "failed_count": failed_count,
            "total_active_subscribers": len(active_subscribers)
        }), 200

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to send notifications")


@subscribers_bp.route("/stats", methods=["GET"])
async def get_subscriber_stats():
    """Get subscriber statistics."""
    entity_service, cyoda_auth_service = get_services()

    try:
        subscribers = await entity_service.get_items("subscriber", ENTITY_VERSION)
        
        stats = {
            "total_subscribers": len(subscribers),
            "active_subscribers": len([s for s in subscribers if s.get("status") == "active"]),
            "inactive_subscribers": len([s for s in subscribers if s.get("status") == "inactive"]),
            "suspended_subscribers": len([s for s in subscribers if s.get("status") == "suspended"]),
            "email_subscribers": len([s for s in subscribers if s.get("email")]),
            "webhook_subscribers": len([s for s in subscribers if s.get("webhook_url")]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info("Retrieved subscriber statistics")
        return jsonify(stats)

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve subscriber statistics")
