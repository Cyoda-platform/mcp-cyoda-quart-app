"""
UI Cart Routes for Cyoda OMS Application

UI-facing REST API endpoints for cart management
as specified in functional requirements.
"""

import logging
import uuid
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from services.services import get_entity_service
from application.entity.cart.version_1.cart import Cart
from application.entity.product.version_1.product import Product

logger = logging.getLogger(__name__)

ui_cart_bp = Blueprint("ui_cart", __name__, url_prefix="/ui")


@ui_cart_bp.route("/cart", methods=["POST"])
async def create_or_get_cart() -> ResponseReturnValue:
    """
    Create or return cart (on first add, initialize NEW→ACTIVE).
    """
    try:
        entity_service = get_entity_service()
        
        # Create new cart
        cart_id = str(uuid.uuid4())
        cart = Cart(
            cartId=cart_id,
            status="NEW",
            lines=[],
            totalItems=0,
            grandTotal=0.0
        )

        # Save the cart
        cart_data = cart.model_dump(by_alias=True)
        response = await entity_service.save(
            entity=cart_data,
            entity_class=Cart.ENTITY_NAME,
            entity_version=str(Cart.ENTITY_VERSION),
        )

        logger.info("Created new cart with ID: %s", response.metadata.id)
        
        # Return cart data
        result_data = response.data
        if hasattr(result_data, "model_dump"):
            result_dict = result_data.model_dump(by_alias=True)
        else:
            result_dict = result_data
            
        return jsonify(result_dict), 201

    except Exception as e:
        logger.exception("Error creating cart: %s", str(e))
        return jsonify({"error": str(e)}), 500


@ui_cart_bp.route("/cart/<cart_id>", methods=["GET"])
async def get_cart(cart_id: str) -> ResponseReturnValue:
    """
    Get cart by ID.
    """
    try:
        if not cart_id or len(cart_id.strip()) == 0:
            return jsonify({"error": "Cart ID is required"}), 400

        entity_service = get_entity_service()

        # Find cart by business ID
        cart_response = await entity_service.find_by_business_id(
            entity_class=Cart.ENTITY_NAME,
            business_id=cart_id,
            business_id_field="cartId",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        if not cart_response:
            return jsonify({"error": "Cart not found"}), 404

        # Return cart data
        cart_data = cart_response.data
        if hasattr(cart_data, "model_dump"):
            cart_dict = cart_data.model_dump(by_alias=True)
        else:
            cart_dict = cart_data

        return jsonify(cart_dict), 200

    except Exception as e:
        logger.exception("Error getting cart %s: %s", cart_id, str(e))
        return jsonify({"error": str(e)}), 500


@ui_cart_bp.route("/cart/<cart_id>/lines", methods=["POST"])
async def add_cart_line(cart_id: str) -> ResponseReturnValue:
    """
    Add/increment line item in cart.
    Body: {sku, qty}
    """
    try:
        if not cart_id or len(cart_id.strip()) == 0:
            return jsonify({"error": "Cart ID is required"}), 400

        data = await request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        sku = data.get("sku")
        qty = data.get("qty", 1)

        if not sku:
            return jsonify({"error": "SKU is required"}), 400
        if qty <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400

        entity_service = get_entity_service()

        # Get product details
        product_response = await entity_service.find_by_business_id(
            entity_class=Product.ENTITY_NAME,
            business_id=sku,
            business_id_field="sku",
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not product_response:
            return jsonify({"error": "Product not found"}), 404

        product_data = product_response.data
        if hasattr(product_data, "model_dump"):
            product_dict = product_data.model_dump(by_alias=True)
        else:
            product_dict = product_data

        # Get cart
        cart_response = await entity_service.find_by_business_id(
            entity_class=Cart.ENTITY_NAME,
            business_id=cart_id,
            business_id_field="cartId",
            entity_version=str(Cart.ENTITY_VERSION),
        )

        if not cart_response:
            return jsonify({"error": "Cart not found"}), 404

        # Update cart with new line item
        cart_data = cart_response.data
        if hasattr(cart_data, "model_dump"):
            cart_dict = cart_data.model_dump(by_alias=True)
        else:
            cart_dict = cart_data

        # Add line item to cart data
        lines = cart_dict.get("lines", [])
        
        # Find existing line or add new one
        found = False
        for line in lines:
            if line.get("sku") == sku:
                line["qty"] += qty
                found = True
                break
        
        if not found:
            lines.append({
                "sku": sku,
                "name": product_dict.get("name"),
                "price": product_dict.get("price"),
                "qty": qty
            })

        cart_dict["lines"] = lines

        # Determine transition based on current status
        transition = None
        if cart_dict.get("status") == "NEW":
            transition = "add_first_item"
            cart_dict["status"] = "ACTIVE"
        else:
            transition = "add_item"

        # Update cart
        updated_response = await entity_service.update(
            entity_id=cart_response.metadata.id,
            entity=cart_dict,
            entity_class=Cart.ENTITY_NAME,
            transition=transition,
            entity_version=str(Cart.ENTITY_VERSION),
        )

        logger.info("Added item %s to cart %s", sku, cart_id)

        # Return updated cart
        result_data = updated_response.data
        if hasattr(result_data, "model_dump"):
            result_dict = result_data.model_dump(by_alias=True)
        else:
            result_dict = result_data

        return jsonify(result_dict), 200

    except Exception as e:
        logger.exception("Error adding line to cart %s: %s", cart_id, str(e))
        return jsonify({"error": str(e)}), 500
