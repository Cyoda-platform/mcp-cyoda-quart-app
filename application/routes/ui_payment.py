"""
UI Payment Routes for Cyoda OMS Application

UI-facing REST API endpoints for payment processing
as specified in functional requirements.
"""

import logging
import uuid
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.cart.version_1.cart import Cart
from application.entity.payment.version_1.payment import Payment
from services.services import get_entity_service

logger = logging.getLogger(__name__)

ui_payment_bp = Blueprint("ui_payment", __name__, url_prefix="/ui")


def _to_dict(data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(data, "model_dump"):
        return data.model_dump(by_alias=True)
    elif hasattr(data, '__dict__'):
        return dict(data)
    else:
        return data


@ui_payment_bp.route("/payment/start", methods=["POST"])
async def start_payment() -> ResponseReturnValue:
    """
    Start payment process.

    Body: {cartId}
    Returns: {paymentId}
    """
    try:
        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        cart_id = data.get("cartId")
        if not cart_id:
            return jsonify({"error": "Cart ID is required"}), 400

        entity_service = get_entity_service()

        # Get cart to validate and get amount
        cart_response = await entity_service.find_by_business_id(
            entity_class=Cart.ENTITY_NAME,
            business_id=cart_id,
            business_id_field="cartId",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        if not cart_response:
            return jsonify({"error": "Cart not found"}), 404

        cart_dict = _to_dict(cart_response.data)

        # Validate cart status
        if cart_dict.get("status") != "CHECKING_OUT":
            return jsonify({"error": "Cart must be in CHECKING_OUT status"}), 400

        # Validate cart has items and guest contact
        if not cart_dict.get("lines") or len(cart_dict.get("lines", [])) == 0:
            return jsonify({"error": "Cart is empty"}), 400

        if not cart_dict.get("guestContact"):
            return jsonify({"error": "Guest contact information is required"}), 400

        # Get cart total
        grand_total = cart_dict.get("grandTotal", 0.0)
        if grand_total <= 0:
            return jsonify({"error": "Cart total must be positive"}), 400

        # Create payment
        payment_id = str(uuid.uuid4())
        payment = Payment(
            paymentId=payment_id,
            cartId=cart_id,
            amount=grand_total,
            status="INITIATED",
            provider="DUMMY",
        )

        # Save payment
        payment_data = payment.model_dump(by_alias=True)
        response = await entity_service.save(
            entity=payment_data,
            entity_class=Payment.ENTITY_NAME,
            entity_version=str(Payment.ENTITY_VERSION),
        )

        logger.info(
            "Started payment %s for cart %s, amount $%.2f",
            payment_id,
            cart_id,
            grand_total,
        )

        return jsonify({"paymentId": payment_id}), 201

    except Exception as e:
        logger.exception("Error starting payment: %s", str(e))
        return jsonify({"error": str(e)}), 500


@ui_payment_bp.route("/payment/<payment_id>", methods=["GET"])
async def get_payment_status(payment_id: str) -> ResponseReturnValue:
    """
    Get payment status for polling.
    """
    try:
        if not payment_id or len(payment_id.strip()) == 0:
            return jsonify({"error": "Payment ID is required"}), 400

        entity_service = get_entity_service()

        # Find payment by business ID
        payment_response = await entity_service.find_by_business_id(
            entity_class=Payment.ENTITY_NAME,
            business_id=payment_id,
            business_id_field="paymentId",
            entity_version=str(Payment.ENTITY_VERSION),
        )

        if not payment_response:
            return jsonify({"error": "Payment not found"}), 404

        # Return payment data
        payment_dict = _to_dict(payment_response.data)

        return jsonify(payment_dict), 200

    except Exception as e:
        logger.exception("Error getting payment status %s: %s", payment_id, str(e))
        return jsonify({"error": str(e)}), 500
