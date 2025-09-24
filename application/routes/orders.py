"""
Order Routes for Purrfect Pets API

Manages all Order-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service
from application.entity.order.version_1.order import Order
from application.models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    OrderListResponse,
    OrderQueryParams,
    OrderResponse,
    OrderSearchResponse,
    OrderUpdateQueryParams,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
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
    """Create a new Order with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Created Order with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
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
    """Get Order by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Order not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
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
    """List Orders with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["state"] = query_args.status

        if query_args.userId:
            search_conditions["userId"] = query_args.userId

        if query_args.petId:
            search_conditions["petId"] = query_args.petId

        if query_args.complete is not None:
            search_conditions["complete"] = str(query_args.complete).lower()

        # Get entities
        if search_conditions:
            # Build search condition request
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

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {
            "orders": paginated_entities,
            "total": len(entity_list),
            "limit": query_args.limit,
            "offset": query_args.offset
        }, 200

    except Exception as e:
        logger.exception("Error listing Orders: %s", str(e))
        return {"error": str(e)}, 500
