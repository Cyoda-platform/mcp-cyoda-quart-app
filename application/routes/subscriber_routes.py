"""
Subscriber routes for the cat fact subscription system.
"""
import logging
from typing import Optional

from quart import Blueprint, request, jsonify, abort
from quart_schema import validate_json, validate_querystring
from pydantic import BaseModel, EmailStr

from service.services import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)

subscriber_bp = Blueprint('subscribers', __name__, url_prefix='/api/subscribers')


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
@validate_json(SubscriberCreateRequest)
async def create_subscriber():
    """Create a new subscriber (sign up for weekly cat facts)."""
    entity_service, cyoda_auth_service = get_services()
    
    data = await request.get_json()
    
    try:
        # Create subscriber entity data
        subscriber_data = {
            "email": data["email"],
            "firstName": data.get("firstName"),
            "lastName": data.get("lastName")
        }
        
        # Save subscriber (triggers initial → pending transition automatically)
        response = await entity_service.save(subscriber_data, "subscriber", ENTITY_VERSION)
        
        # Return response with technical ID
        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive", False),
            "state": response.state
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
        response = await entity_service.get_by_id(subscriber_id, "subscriber", ENTITY_VERSION)
        
        result = {
            "id": response.technical_id,
            "email": response.data.get("email"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "subscriptionDate": response.data.get("subscriptionDate"),
            "isActive": response.data.get("isActive"),
            "state": response.state
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.exception(f"Failed to get subscriber {subscriber_id}: {e}")
        abort(404)
