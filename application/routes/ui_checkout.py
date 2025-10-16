"""
UI Checkout Routes for Cyoda OMS Application

UI-facing REST API endpoints for checkout process
as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.cart.version_1.cart import Cart
from services.services import get_entity_service

logger = logging.getLogger(__name__)

ui_checkout_bp = Blueprint("ui_checkout", __name__, url_prefix="/ui")


@ui_checkout_bp.route("/checkout/<cart_id>", methods=["POST"])
async def checkout(cart_id: str) -> ResponseReturnValue:
    """
    Checkout process - attach guest contact to cart.

    Body:
    {
        "guestContact": {
            "name": "string",
            "email": "string?",
            "phone": "string?",
            "address": {
                "line1": "...",
                "city": "...",
                "postcode": "...",
                "country": "..."
            }
        }
    }
    """
    try:
        if not cart_id or len(cart_id.strip()) == 0:
            return jsonify({"error": "Cart ID is required"}), 400

        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        guest_contact = data.get("guestContact")
        if not guest_contact:
            return jsonify({"error": "Guest contact information is required"}), 400

        # Validate guest contact
        if not guest_contact.get("name"):
            return jsonify({"error": "Guest name is required"}), 400

        address = guest_contact.get("address", {})
        if not address:
            return jsonify({"error": "Guest address is required"}), 400

        required_address_fields = ["line1", "city", "postcode", "country"]
        for field in required_address_fields:
            if not address.get(field):
                return jsonify({"error": f"Address {field} is required"}), 400

        entity_service = get_entity_service()

        # Get cart
        cart_response = await entity_service.find_by_business_id(
            entity_class=Cart.ENTITY_NAME,
            business_id=cart_id,
            business_id_field="cartId",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        if not cart_response:
            return jsonify({"error": "Cart not found"}), 404

        # Update cart with guest contact
        cart_data = cart_response.data
        if hasattr(cart_data, "model_dump"):
            cart_dict = cart_data.model_dump(by_alias=True)
        else:
            cart_dict = cart_data

        # Validate cart status
        if cart_dict.get("status") != "CHECKING_OUT":
            return jsonify({"error": "Cart must be in CHECKING_OUT status"}), 400

        # Validate cart has items
        if not cart_dict.get("lines") or len(cart_dict.get("lines", [])) == 0:
            return jsonify({"error": "Cart is empty"}), 400

        cart_dict["guestContact"] = guest_contact

        # Update cart
        updated_response = await entity_service.update(
            entity_id=cart_response.metadata.id,
            entity=cart_dict,
            entity_class=Cart.ENTITY_NAME,
            entity_version=str(Cart.ENTITY_VERSION),
        )

        logger.info("Updated cart %s with guest contact", cart_id)

        # Return updated cart
        result_data = updated_response.data
        if hasattr(result_data, "model_dump"):
            result_dict = result_data.model_dump(by_alias=True)
        else:
            result_dict = result_data

        return jsonify(result_dict), 200

    except Exception as e:
        logger.exception("Error in checkout for cart %s: %s", cart_id, str(e))
        return jsonify({"error": str(e)}), 500
