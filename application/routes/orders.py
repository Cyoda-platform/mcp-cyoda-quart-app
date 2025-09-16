"""
Order Routes for Purrfect Pets API

Manages all Order-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.order.version_1.order import Order
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("", methods=["GET"])
@tag(["orders"])
@operation_id("get_orders")
async def get_orders() -> ResponseReturnValue:
    """Get all orders for current user"""
    try:
        service = get_entity_service()

        # Get query parameters
        status = request.args.get("status")

        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if status:
            search_conditions["state"] = status

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Order.ENTITY_NAME,
                condition=condition,
                entity_version=str(Order.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Order.ENTITY_NAME,
                entity_version=str(Order.ENTITY_VERSION),
            )

        # Convert to response format
        orders_data = []
        for entity_response in entities:
            order_data = _to_entity_dict(entity_response.data)
            order_data["status"] = entity_response.metadata.state
            orders_data.append(order_data)

        return jsonify(orders_data), 200

    except Exception as e:
        logger.exception("Error getting orders: %s", str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<order_id>", methods=["GET"])
@tag(["orders"])
@operation_id("get_order")
async def get_order(order_id: str) -> ResponseReturnValue:
    """Get order by ID"""
    try:
        service = get_entity_service()

        response = await service.get_by_id(
            entity_id=order_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Order not found"}), 404

        order_data = _to_entity_dict(response.data)
        order_data["status"] = response.metadata.state

        return jsonify(order_data), 200

    except Exception as e:
        logger.exception("Error getting order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("", methods=["POST"])
@tag(["orders"])
@operation_id("create_order")
async def create_order() -> ResponseReturnValue:
    """Create new order"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Create Order entity from request data
        order = Order(**data)
        entity_data = order.model_dump(by_alias=True)

        # Save the entity (will trigger automatic transition to placed)
        response = await service.save(
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Created Order with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "user_id": order.user_id,
                    "status": response.metadata.state,
                    "message": "Order created successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        logger.warning("Validation error creating order: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error creating order: %s", str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<order_id>", methods=["PUT"])
@tag(["orders"])
@operation_id("update_order")
async def update_order(order_id: str) -> ResponseReturnValue:
    """Update order"""
    try:
        service = get_entity_service()
        data = await request.get_json()

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Map transition names to workflow transition names
        transition_map = {
            "approve": "transition_to_approved",
            "ship": "transition_to_shipped",
            "deliver": "transition_to_delivered",
            "cancel": "transition_to_cancelled_from_placed",  # Default cancel transition
        }

        workflow_transition = None
        if transition:
            workflow_transition = transition_map.get(transition)
            if not workflow_transition:
                return jsonify({"error": f"Invalid transition: {transition}"}), 400

        # Create Order entity from request data for validation
        order = Order(**data)
        entity_data = order.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=order_id,
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            transition=workflow_transition,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Updated Order %s", order_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "status": response.metadata.state,
                    "message": f"Order updated{' and ' + transition if transition else ''} successfully",
                }
            ),
            200,
        )

    except ValueError as e:
        logger.warning("Validation error updating order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error updating order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<order_id>", methods=["DELETE"])
@tag(["orders"])
@operation_id("cancel_order")
async def cancel_order(order_id: str) -> ResponseReturnValue:
    """Cancel order"""
    try:
        service = get_entity_service()

        # Get transition from query parameters (required for cancel)
        transition = request.args.get("transition")
        if transition != "cancel":
            return (
                jsonify(
                    {"error": "Transition 'cancel' is required for DELETE operation"}
                ),
                400,
            )

        # Execute cancel transition
        response = await service.execute_transition(
            entity_id=order_id,
            transition="transition_to_cancelled_from_placed",
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Cancelled Order %s", order_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "status": response.metadata.state,
                    "message": "Order cancelled successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error cancelling order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500
