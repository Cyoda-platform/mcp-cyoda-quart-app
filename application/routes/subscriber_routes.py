"""
Subscriber routes for the cat fact subscription system.
"""

import logging
from typing import Optional

from pydantic import BaseModel, EmailStr
from quart import Blueprint, abort, jsonify, request
from quart_schema import validate_request, validate_querystring

from common.config.config import ENTITY_VERSION
from service.services import get_auth_service, get_entity_service

logger = logging.getLogger(__name__)

subscriber_bp = Blueprint("subscribers", __name__, url_prefix="/api/subscribers")


class SubscriberCreateRequest(BaseModel):
    """Request model for creating a subscriber."""

    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class SubscriberUpdateRequest(BaseModel):
    """Request model for updating a subscriber."""

    firstName: Optional[str] = None
    lastName: Optional[str] = None
    transitionName: Optional[str] = None


class SubscriberTransitionRequest(BaseModel):
    """Request model for subscriber transitions."""

    transitionName: str


class SubscriberQuery(BaseModel):
    """Query parameters for listing subscribers."""

    state: Optional[str] = None
    page: int = 0
    size: int = 20


def get_services():
    """Get services from the registry lazily."""
    return get_entity_service(), get_auth_service()


@subscriber_bp.route("", methods=["POST"])
@validate_request(SubscriberCreateRequest)
async def create_subscriber():
    """Create a new subscriber (sign up for weekly cat facts)."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Create subscriber entity data
        subscriber_data = {
            "email": data["email"],
            "firstName": data.get("firstName"),
            "lastName": data.get("lastName"),
        }

        # Save subscriber (triggers initial → pending transition automatically)
        response = await entity_service.save(
            subscriber_data, "subscriber", ENTITY_VERSION
        )

        # Return response with technical ID
        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive", False),
            "state": response.state,
        }

        return jsonify(result), 201

    except Exception as e:
        logger.exception(f"Failed to create subscriber: {e}")
        return jsonify({"error": "Failed to create subscriber"}), 500


@subscriber_bp.route("/<subscriber_id>", methods=["GET"])
async def get_subscriber(subscriber_id: str):
    """Get subscriber details by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        response = await entity_service.get_by_id(
            subscriber_id, "subscriber", ENTITY_VERSION
        )

        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get subscriber {subscriber_id}: {e}")
        abort(404)


@subscriber_bp.route("/<subscriber_id>", methods=["PUT"])
@validate_request(SubscriberUpdateRequest)
async def update_subscriber(subscriber_id: str):
    """Update subscriber information."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current subscriber
        current_response = await entity_service.get_by_id(
            subscriber_id, "subscriber", ENTITY_VERSION
        )

        # Update data
        updated_data = current_response.data.copy()
        if data.get("firstName") is not None:
            updated_data["firstName"] = data["firstName"]
        if data.get("lastName") is not None:
            updated_data["lastName"] = data["lastName"]

        # Update subscriber (no state change)
        response = await entity_service.update(
            subscriber_id,
            updated_data,
            "subscriber",
            transition=data.get("transitionName"),
            entity_version=ENTITY_VERSION,
        )

        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to update subscriber {subscriber_id}: {e}")
        return jsonify({"error": "Failed to update subscriber"}), 500


@subscriber_bp.route("/<subscriber_id>/activate", methods=["PUT"])
@validate_request(SubscriberTransitionRequest)
async def activate_subscriber(subscriber_id: str):
    """Activate a pending subscriber."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current subscriber
        current_response = await entity_service.get_by_id(
            subscriber_id, "subscriber", ENTITY_VERSION
        )

        # Update with transition
        response = await entity_service.update(
            subscriber_id,
            current_response.data,
            "subscriber",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION,
        )

        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "isActive": response.data.get("isActive"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to activate subscriber {subscriber_id}: {e}")
        return jsonify({"error": "Failed to activate subscriber"}), 500


@subscriber_bp.route("/<subscriber_id>/unsubscribe", methods=["PUT"])
@validate_request(SubscriberTransitionRequest)
async def unsubscribe_subscriber(subscriber_id: str):
    """Unsubscribe a subscriber."""
    entity_service, cyoda_auth_service = get_services()

    data = await request.get_json()

    try:
        # Get current subscriber
        current_response = await entity_service.get_by_id(
            subscriber_id, "subscriber", ENTITY_VERSION
        )

        # Update with transition
        response = await entity_service.update(
            subscriber_id,
            current_response.data,
            "subscriber",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION,
        )

        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "isActive": response.data.get("isActive"),
            "state": response.state,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to unsubscribe subscriber {subscriber_id}: {e}")
        return jsonify({"error": "Failed to unsubscribe subscriber"}), 500


@subscriber_bp.route("/unsubscribe/<token>", methods=["GET"])
async def unsubscribe_via_token(token: str):
    """Unsubscribe via email link using unsubscribe token."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find subscriber by unsubscribe token
        subscribers = await entity_service.find_all("subscriber", ENTITY_VERSION)
        target_subscriber = None

        for subscriber in subscribers:
            if subscriber.data.get("unsubscribeToken") == token:
                target_subscriber = subscriber
                break

        if not target_subscriber:
            abort(404)

        # Update with unsubscribe transition
        response = await entity_service.update(
            target_subscriber.technical_id,
            target_subscriber.data,
            "subscriber",
            transition="active_to_unsubscribed",
            entity_version=ENTITY_VERSION,
        )

        result = {
            "message": "Successfully unsubscribed",
            "email": response.data.get("email"),
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to unsubscribe via token {token}: {e}")
        return jsonify({"error": "Failed to unsubscribe"}), 500


@subscriber_bp.route("", methods=["GET"])
@validate_querystring(SubscriberQuery)
async def get_subscribers():
    """Get all subscribers with optional filtering."""
    entity_service, cyoda_auth_service = get_services()

    args = SubscriberQuery(**request.args)

    try:
        # Get all subscribers
        subscribers = await entity_service.find_all("subscriber", ENTITY_VERSION)

        # Apply state filter
        if args.state:
            subscribers = [s for s in subscribers if s.state == args.state]

        # Apply pagination
        total_elements = len(subscribers)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_subscribers = subscribers[start_idx:end_idx]

        # Format response
        content = []
        for subscriber in paginated_subscribers:
            content.append(
                {
                    "id": subscriber.technical_id,
                    "email": subscriber.data.get("email"),
                    "firstName": subscriber.data.get("firstName"),
                    "lastName": subscriber.data.get("lastName"),
                    "isActive": subscriber.data.get("isActive"),
                    "state": subscriber.state,
                }
            )

        result = {
            "content": content,
            "totalElements": total_elements,
            "totalPages": (total_elements + args.size - 1) // args.size,
            "size": args.size,
            "number": args.page,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get subscribers: {e}")
        return jsonify({"error": "Failed to get subscribers"}), 500
