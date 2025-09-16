"""Order routes for Purrfect Pets API."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from quart import Blueprint, abort, jsonify, request
from quart_schema import validate_querystring, validate_request

from application.entity.order.version_1.order import Order
from service.services import get_auth_service, get_entity_service

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

ENTITY_VERSION = "1"


class OrderQuery(BaseModel):
    """Query parameters for order filtering."""

    page: Optional[int] = Field(0, ge=0, description="Page number")
    size: Optional[int] = Field(10, ge=1, le=100, description="Page size")
    status: Optional[str] = Field(None, description="Filter by order status")
    ownerId: Optional[int] = Field(None, description="Filter by owner ID")


class OrderRequest(BaseModel):
    """Request model for creating orders."""

    ownerId: int = Field(..., description="Owner ID")
    petId: int = Field(..., description="Pet ID")
    quantity: int = Field(1, ge=1, description="Order quantity")
    totalAmount: float = Field(..., gt=0, description="Total order amount")
    deliveryAddress: str = Field(..., description="Delivery address")
    notes: Optional[str] = Field(None, description="Special instructions")


class OrderUpdateRequest(BaseModel):
    """Request model for updating orders."""

    transitionName: Optional[str] = Field(None, description="Workflow transition name")
    deliveryAddress: Optional[str] = Field(None, description="Delivery address")
    notes: Optional[str] = Field(None, description="Special instructions")
    trackingInfo: Optional[dict] = Field(None, description="Tracking information")


def get_services():
    """Get entity service and auth service."""
    return get_entity_service(), get_auth_service()


@orders_bp.route("", methods=["GET"])
@validate_querystring(OrderQuery)
async def get_orders():
    """Get all orders with pagination."""
    entity_service, cyoda_auth_service = get_services()
    args = OrderQuery(**request.args)

    try:
        # Get all orders from entity service
        orders_response = await entity_service.find_all("Order", ENTITY_VERSION)
        orders = orders_response if orders_response else []

        # Apply filters
        filtered_orders = []
        for order_data in orders:
            order = Order(**order_data) if isinstance(order_data, dict) else order_data

            # Apply status filter (map to state)
            if args.status:
                status_map = {
                    "PLACED": "placed",
                    "CONFIRMED": "confirmed",
                    "PREPARING": "preparing",
                    "SHIPPED": "shipped",
                    "DELIVERED": "delivered",
                    "CANCELLED": "cancelled",
                    "RETURNED": "returned",
                }
                expected_state = status_map.get(args.status.upper())
                if expected_state and order.state != expected_state:
                    continue

            # Apply owner filter
            if args.ownerId and order.ownerId != args.ownerId:
                continue

            filtered_orders.append(order)

        # Apply pagination
        total_elements = len(filtered_orders)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_orders = filtered_orders[start_idx:end_idx]

        # Convert to response format
        content = []
        for order in paginated_orders:
            content.append(
                {
                    "id": order.id,
                    "ownerId": order.ownerId,
                    "petId": order.petId,
                    "totalAmount": order.totalAmount,
                    "orderDate": order.orderDate,
                    "state": order.state.upper() if order.state else "UNKNOWN",
                }
            )

        response = {"content": content, "totalElements": total_elements}

        logger.info(f"Retrieved {len(content)} orders (page {args.page})")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to get orders: {e}")
        return jsonify({"error": f"Failed to get orders: {str(e)}"}), 500


@orders_bp.route("/<int:order_id>", methods=["GET"])
async def get_order(order_id: int):
    """Get order by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find order by business ID
        order_response = await entity_service.find_by_business_id(
            "Order", str(order_id), "id", ENTITY_VERSION
        )

        if not order_response:
            return jsonify({"error": "Order not found"}), 404

        order_data = order_response.entity
        order = Order(**order_data) if isinstance(order_data, dict) else order_data

        response = {
            "id": order.id,
            "ownerId": order.ownerId,
            "petId": order.petId,
            "quantity": order.quantity,
            "totalAmount": order.totalAmount,
            "orderDate": order.orderDate,
            "deliveryDate": order.deliveryDate,
            "deliveryAddress": order.deliveryAddress,
            "notes": order.notes,
            "state": order.state.upper() if order.state else "UNKNOWN",
            "createdAt": order.createdAt,
            "updatedAt": order.updatedAt,
        }

        logger.info(f"Retrieved order {order_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to get order {order_id}: {e}")
        return jsonify({"error": f"Failed to get order: {str(e)}"}), 500


@orders_bp.route("", methods=["POST"])
@validate_request(OrderRequest)
async def create_order(data: OrderRequest):
    """Create new order."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Generate unique ID
        order_id = len(await entity_service.find_all("Order", ENTITY_VERSION) or []) + 1

        # Create order entity
        order_data = {
            "id": order_id,
            "ownerId": data.ownerId,
            "petId": data.petId,
            "quantity": data.quantity,
            "totalAmount": data.totalAmount,
            "deliveryAddress": data.deliveryAddress,
            "notes": data.notes,
            "state": "initial_state",
        }

        # Save order
        order_response = await entity_service.save(order_data, "Order", ENTITY_VERSION)

        response = {
            "id": order_id,
            "ownerId": data.ownerId,
            "petId": data.petId,
            "totalAmount": data.totalAmount,
            "state": "PLACED",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Created order {order_id}")
        return jsonify(response), 201

    except Exception as e:
        logger.exception(f"Failed to create order: {e}")
        return jsonify({"error": f"Failed to create order: {str(e)}"}), 500


@orders_bp.route("/<int:order_id>", methods=["PUT"])
@validate_request(OrderUpdateRequest)
async def update_order(order_id: int, data: OrderUpdateRequest):
    """Update order."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing order
        order_response = await entity_service.find_by_business_id(
            "Order", str(order_id), "id", ENTITY_VERSION
        )

        if not order_response:
            return jsonify({"error": "Order not found"}), 404

        # Update fields if provided
        update_data = {}
        if data.deliveryAddress is not None:
            update_data["deliveryAddress"] = data.deliveryAddress
        if data.notes is not None:
            update_data["notes"] = data.notes
        if data.trackingInfo is not None:
            update_data["trackingInfo"] = data.trackingInfo

        # Add timestamp
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        # Update with transition if provided
        transition = data.transitionName
        if transition:
            # Map transition names to workflow transitions
            transition_map = {
                "CONFIRM": "transition_to_confirmed",
                "PREPARE": "transition_to_preparing",
                "SHIP": "transition_to_shipped",
                "DELIVER": "transition_to_delivered",
                "CANCEL": "transition_to_cancelled_from_placed",
                "CANCEL_CONFIRMED": "transition_to_cancelled_from_confirmed",
                "RETURN": "transition_to_returned",
            }
            workflow_transition = transition_map.get(transition)
        else:
            workflow_transition = None

        # Update order
        updated_response = await entity_service.update(
            order_response.metadata.id,
            update_data,
            "Order",
            workflow_transition,
            ENTITY_VERSION,
        )

        # Get updated state
        updated_order_data = updated_response.entity
        updated_order = (
            Order(**updated_order_data)
            if isinstance(updated_order_data, dict)
            else updated_order_data
        )

        response = {
            "id": order_id,
            "state": updated_order.state.upper() if updated_order.state else "UNKNOWN",
            "updatedAt": updated_order.updatedAt,
        }

        logger.info(f"Updated order {order_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to update order {order_id}: {e}")
        return jsonify({"error": f"Failed to update order: {str(e)}"}), 500


@orders_bp.route("/<int:order_id>", methods=["DELETE"])
async def delete_order(order_id: int):
    """Delete order (cancel)."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing order
        order_response = await entity_service.find_by_business_id(
            "Order", str(order_id), "id", ENTITY_VERSION
        )

        if not order_response:
            return jsonify({"error": "Order not found"}), 404

        # Cancel by updating state
        delete_data = {"updatedAt": datetime.now(timezone.utc).isoformat()}

        await entity_service.update(
            order_response.metadata.id,
            delete_data,
            "Order",
            "transition_to_cancelled_from_placed",  # Cancel transition
            ENTITY_VERSION,
        )

        response = {"message": "Order deleted successfully"}

        logger.info(f"Deleted order {order_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to delete order {order_id}: {e}")
        return jsonify({"error": f"Failed to delete order: {str(e)}"}), 500
