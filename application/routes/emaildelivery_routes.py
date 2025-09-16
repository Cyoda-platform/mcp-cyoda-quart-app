"""
EmailDelivery routes for the cat fact subscription system.
"""
import logging
from typing import Optional

from quart import Blueprint, request, jsonify, abort
from quart_schema import validate_json, validate_querystring
from pydantic import BaseModel

from service.services import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)

emaildelivery_bp = Blueprint('email_deliveries', __name__, url_prefix='/api/email-deliveries')


class EmailDeliveryTransitionRequest(BaseModel):
    """Request model for email delivery transitions."""
    transitionName: str


class EmailDeliveryQuery(BaseModel):
    """Query parameters for listing email deliveries."""
    subscriberId: Optional[int] = None
    catFactId: Optional[int] = None
    state: Optional[str] = None
    page: int = 0
    size: int = 20


def get_services():
    """Get services from the registry lazily."""
    return get_entity_service(), get_auth_service()


@emaildelivery_bp.route("/<delivery_id>", methods=["GET"])
async def get_emaildelivery(delivery_id: str):
    """Get email delivery details by ID."""
    entity_service, cyoda_auth_service = get_services()
    
    try:
        response = await entity_service.get_by_id(delivery_id, "emaildelivery", ENTITY_VERSION)
        
        result = {
            "id": response.technical_id,
            "subscriberId": response.data.get("subscriberId"),
            "catFactId": response.data.get("catFactId"),
            "sentDate": response.data.get("sentDate"),
            "deliveryAttempts": response.data.get("deliveryAttempts"),
            "opened": response.data.get("opened"),
            "openedDate": response.data.get("openedDate"),
            "state": response.state
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.exception(f"Failed to get email delivery {delivery_id}: {e}")
        abort(404)


@emaildelivery_bp.route("/<delivery_id>/retry", methods=["PUT"])
@validate_json(EmailDeliveryTransitionRequest)
async def retry_emaildelivery(delivery_id: str):
    """Retry failed email delivery."""
    entity_service, cyoda_auth_service = get_services()
    
    data = await request.get_json()
    
    try:
        # Get current email delivery
        current_response = await entity_service.get_by_id(delivery_id, "emaildelivery", ENTITY_VERSION)
        
        # Update with retry transition
        response = await entity_service.update(
            delivery_id,
            current_response.data,
            "emaildelivery",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION
        )
        
        result = {
            "id": response.technical_id,
            "subscriberId": response.data.get("subscriberId"),
            "catFactId": response.data.get("catFactId"),
            "deliveryAttempts": response.data.get("deliveryAttempts"),
            "state": response.state
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.exception(f"Failed to retry email delivery {delivery_id}: {e}")
        return jsonify({"error": "Failed to retry email delivery"}), 500


@emaildelivery_bp.route("/<delivery_id>/mark-opened", methods=["PUT"])
@validate_json(EmailDeliveryTransitionRequest)
async def mark_emaildelivery_opened(delivery_id: str):
    """Mark email as opened (tracking endpoint)."""
    entity_service, cyoda_auth_service = get_services()
    
    data = await request.get_json()
    
    try:
        # Get current email delivery
        current_response = await entity_service.get_by_id(delivery_id, "emaildelivery", ENTITY_VERSION)
        
        # Update with open transition
        response = await entity_service.update(
            delivery_id,
            current_response.data,
            "emaildelivery",
            transition=data["transitionName"],
            entity_version=ENTITY_VERSION
        )
        
        result = {
            "id": response.technical_id,
            "opened": response.data.get("opened"),
            "openedDate": response.data.get("openedDate"),
            "state": response.state
        }
        
        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to mark email delivery opened {delivery_id}: {e}")
        return jsonify({"error": "Failed to mark email as opened"}), 500


@emaildelivery_bp.route("", methods=["GET"])
@validate_querystring(EmailDeliveryQuery)
async def get_emaildeliveries():
    """Get email deliveries with filtering."""
    entity_service, cyoda_auth_service = get_services()

    args = EmailDeliveryQuery(**request.args)

    try:
        # Get all email deliveries
        deliveries = await entity_service.find_all("emaildelivery", ENTITY_VERSION)

        # Apply filters
        if args.subscriberId:
            deliveries = [d for d in deliveries if d.data.get("subscriberId") == args.subscriberId]

        if args.catFactId:
            deliveries = [d for d in deliveries if d.data.get("catFactId") == args.catFactId]

        if args.state:
            deliveries = [d for d in deliveries if d.state == args.state]

        # Apply pagination
        total_elements = len(deliveries)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_deliveries = deliveries[start_idx:end_idx]

        # Format response
        content = []
        for delivery in paginated_deliveries:
            content.append({
                "id": delivery.technical_id,
                "subscriberId": delivery.data.get("subscriberId"),
                "catFactId": delivery.data.get("catFactId"),
                "sentDate": delivery.data.get("sentDate"),
                "opened": delivery.data.get("opened"),
                "state": delivery.state
            })

        result = {
            "content": content,
            "totalElements": total_elements,
            "totalPages": (total_elements + args.size - 1) // args.size
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get email deliveries: {e}")
        return jsonify({"error": "Failed to get email deliveries"}), 500
