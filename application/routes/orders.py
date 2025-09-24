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

from application.entity.order.version_1.order import Order
from application.models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    OrderListResponse,
    OrderQueryParams,
    OrderResponse,
    OrderSearchResponse,
    OrderUpdateQueryParams,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


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
            "offset": query_args.offset,
        }, 200

    except Exception as e:
        logger.exception("Error listing Orders: %s", str(e))
        return {"error": str(e)}, 500


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
    """Update Order and optionally trigger workflow transition with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Order.ENTITY_NAME,
            transition=transition,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Updated Order %s", entity_id)

        # Return updated entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Order %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Order %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


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
    """Delete Order with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info("Deleted Order %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Order deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Order %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@orders_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["orders"])
@operation_id("check_order_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Order exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Order existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


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
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting Orders: %s", str(e))
        return {"error": str(e)}, 500


@orders_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["orders"])
@operation_id("get_order_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Order"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for Order %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@orders_bp.route("/search", methods=["POST"])
@tag(["orders"])
@operation_id("search_orders")
@validate(
    request=SearchRequest,
    responses={
        200: (OrderSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Orders using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Order.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Order.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"orders": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Orders: %s", str(e))
        return {"error": str(e)}, 500


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
    """Trigger a specific workflow transition with validation"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "Order not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Order.ENTITY_NAME,
            entity_version=str(Order.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Order %s", data.transition_name, entity_id
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception(
            "Error executing transition on Order %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500
