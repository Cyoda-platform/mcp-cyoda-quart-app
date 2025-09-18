"""
Order Routes for Cyoda Client Application

Manages all Order-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

from ..entity.order.version_1.order import Order
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    OrderListResponse,
    OrderQueryParams,
    OrderResponse,
    OrderUpdateQueryParams,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.route("", methods=["POST"])
@tag(["orders"])
@operation_id("create_order")
@validate(
    request=Order,
    responses={
        201: (OrderResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_order(data: Order) -> ResponseReturnValue:
    """Create a new Order"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )
        logger.info("Created Order with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Order: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Order: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@orders_bp.route("/<entity_id>", methods=["GET"])
@tag(["orders"])
@operation_id("get_order")
@validate(
    responses={
        200: (OrderResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_order(entity_id: str) -> ResponseReturnValue:
    """Get Order by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Order not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Order %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@orders_bp.route("", methods=["GET"])
@validate_querystring(OrderQueryParams)
@tag(["orders"])
@operation_id("list_orders")
@validate(
    responses={
        200: (OrderListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_orders(query_args: OrderQueryParams) -> ResponseReturnValue:
    """List Orders with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["state"] = query_args.status
        if query_args.user_id:
            search_conditions["userId"] = query_args.user_id
        if query_args.pet_id:
            search_conditions["petId"] = query_args.pet_id

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

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Orders: %s", str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(OrderUpdateQueryParams)
@tag(["orders"])
@operation_id("update_order")
@validate(
    request=Order,
    responses={
        200: (OrderResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_order(
    entity_id: str, data: Order, query_args: OrderUpdateQueryParams
) -> ResponseReturnValue:
    """Update Order and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            transition=transition,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Updated Order %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Order %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Order %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@orders_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["orders"])
@operation_id("delete_order")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_order(entity_id: str) -> ResponseReturnValue:
    """Delete Order"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Deleted Order %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Order deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Order %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@orders_bp.route("/count", methods=["GET"])
@tag(["orders"])
@operation_id("count_orders")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Orders"""
    try:
        count = await service.count(
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Orders: %s", str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["orders"])
@operation_id("trigger_order_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Order not found"}), 404

        previous_state = current_entity.metadata.state

        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Executed transition '%s' on Order %s", data.transition_name, entity_id)

        return jsonify({
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }), 200
    except Exception as e:
        logger.exception("Error executing transition on Order %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
