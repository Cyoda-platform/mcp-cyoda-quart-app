"""
UI Order Routes for Cyoda OMS Application

UI-facing REST API endpoints for order management
as specified in functional requirements.
"""

import logging
import uuid
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.cart.version_1.cart import Cart
from application.entity.order.version_1.order import Order
from application.entity.payment.version_1.payment import Payment
from services.services import get_entity_service

logger = logging.getLogger(__name__)

ui_order_bp = Blueprint("ui_order", __name__, url_prefix="/ui")


def _generate_order_number() -> str:
    """Generate a short ULID-style order number"""
    # For demo purposes, generate a simple order number
    import random
    import string
    import time

    # Use timestamp and random chars for uniqueness
    timestamp = int(time.time())
    random_chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"O-{timestamp % 100000}-{random_chars}"


@ui_order_bp.route("/order/create", methods=["POST"])
async def create_order() -> ResponseReturnValue:
    """
    Create order from paid cart.

    Body: {paymentId, cartId}
    Preconditions: Payment PAID
    Returns: {orderId, orderNumber, status}
    """
    try:
        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        payment_id = data.get("paymentId")
        cart_id = data.get("cartId")

        if not payment_id:
            return jsonify({"error": "Payment ID is required"}), 400
        if not cart_id:
            return jsonify({"error": "Cart ID is required"}), 400

        entity_service = get_entity_service()

        # Get and validate payment
        payment_response = await entity_service.find_by_business_id(
            entity_class=Payment.ENTITY_NAME,
            business_id=payment_id,
            business_id_field="paymentId",
            entity_version=str(Payment.ENTITY_VERSION),
        )

        if not payment_response:
            return jsonify({"error": "Payment not found"}), 404

        payment_data = payment_response.data
        if hasattr(payment_data, "model_dump"):
            payment_dict = payment_data.model_dump(by_alias=True)
        else:
            payment_dict = payment_data

        # Validate payment is PAID
        if payment_dict.get("status") != "PAID":
            return jsonify({"error": "Payment must be PAID to create order"}), 400

        # Get cart
        cart_response = await entity_service.find_by_business_id(
            entity_class=Cart.ENTITY_NAME,
            business_id=cart_id,
            business_id_field="cartId",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        if not cart_response:
            return jsonify({"error": "Cart not found"}), 404

        cart_data = cart_response.data
        if hasattr(cart_data, "model_dump"):
            cart_dict = cart_data.model_dump(by_alias=True)
        else:
            cart_dict = cart_data

        # Validate cart has guest contact
        if not cart_dict.get("guestContact"):
            return jsonify({"error": "Cart must have guest contact information"}), 400

        # Create order
        order_id = str(uuid.uuid4())
        order_number = _generate_order_number()

        order = Order.create_from_cart_and_payment(
            order_id=order_id,
            order_number=order_number,
            cart_data=cart_dict,
            payment_data=payment_dict,
        )

        # Save order
        order_data = order.model_dump(by_alias=True)
        response = await entity_service.save(
            entity=order_data,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        # Update cart status to CONVERTED
        cart_dict["status"] = "CONVERTED"
        await entity_service.update(
            entity_id=cart_response.metadata.id,
            entity=cart_dict,
            entity_class=Cart.ENTITY_NAME,
            transition="checkout",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        logger.info(
            "Created order %s from cart %s and payment %s",
            order_number,
            cart_id,
            payment_id,
        )

        return (
            jsonify(
                {
                    "orderId": order_id,
                    "orderNumber": order_number,
                    "status": "WAITING_TO_FULFILL",
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating order: %s", str(e))
        return jsonify({"error": str(e)}), 500


@ui_order_bp.route("/order/<order_id>", methods=["GET"])
async def get_order(order_id: str) -> ResponseReturnValue:
    """
    Get order by ID for confirmation/status.
    """
    try:
        if not order_id or len(order_id.strip()) == 0:
            return jsonify({"error": "Order ID is required"}), 400

        entity_service = get_entity_service()

        # Find order by business ID
        order_response = await entity_service.find_by_business_id(
            entity_class=Order.ENTITY_NAME,
            business_id=order_id,
            business_id_field="orderId",
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not order_response:
            return jsonify({"error": "Order not found"}), 404

        # Return order data
        order_data = order_response.data
        if hasattr(order_data, "model_dump"):
            order_dict = order_data.model_dump(by_alias=True)
        else:
            order_dict = order_data

        return jsonify(order_dict), 200

    except Exception as e:
        logger.exception("Error getting order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500
