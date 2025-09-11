"""
Order Routes for Purrfect Pets API

Manages all Order-related API endpoints as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_request

from services.services import get_entity_service

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...


entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


class OrderItemRequest(BaseModel):
    pet_id: int = Field(..., alias="petId", description="Pet ID")
    quantity: int = Field(default=1, description="Quantity")


class AddressRequest(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State or province")
    zip_code: str = Field(..., alias="zipCode", description="ZIP code")
    country: str = Field(..., description="Country name")


class OrderCreateRequest(BaseModel):
    user_id: int = Field(..., alias="userId", description="User ID")
    items: List[OrderItemRequest] = Field(..., description="Order items")
    shipping_address: AddressRequest = Field(
        ..., alias="shippingAddress", description="Shipping address"
    )
    payment_method: str = Field(
        ..., alias="paymentMethod", description="Payment method"
    )
    notes: Optional[str] = Field(default=None, description="Order notes")


class OrderUpdateRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Order notes")


@orders_bp.route("", methods=["POST"])
@validate_request(OrderCreateRequest)
async def create_order(data: OrderCreateRequest) -> ResponseReturnValue:
    """Create a new order"""
    try:
        service = get_services()
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data, entity_class="Order", entity_version="1"
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "userId": entity_data.get("userId"),
                    "status": _map_state_to_status(response.metadata.state),
                    "totalAmount": 0.0,  # Would be calculated by processor
                    "orderDate": None,  # Would be set by processor
                    "message": "Order created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating order: %s", str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<order_id>", methods=["GET"])
async def get_order(order_id: str) -> ResponseReturnValue:
    """Get order by ID"""
    try:
        service = get_services()
        response = await service.get_by_id(
            entity_id=order_id, entity_class="Order", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Order not found"}), 404

        order_data = {
            "id": response.metadata.id,
            "userId": response.data.get("userId"),
            "status": _map_state_to_status(response.metadata.state),
            "orderDate": response.data.get("orderDate"),
            "totalAmount": response.data.get("totalAmount"),
            "items": response.data.get("items", []),
            "shippingAddress": response.data.get("shippingAddress"),
        }

        return jsonify(order_data), 200

    except Exception as e:
        logger.exception("Error getting order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<order_id>", methods=["PUT"])
@validate_request(OrderUpdateRequest)
async def update_order(order_id: str, data: OrderUpdateRequest) -> ResponseReturnValue:
    """Update order status"""
    try:
        service = get_services()
        transition: Optional[str] = request.args.get("transitionName")

        if not transition:
            return jsonify({"error": "transitionName is required"}), 400

        entity_data: Dict[str, Any] = {
            k: v for k, v in data.model_dump(exclude_none=True).items()
        }

        response = await service.update(
            entity_id=order_id,
            entity=entity_data,
            entity_class="Order",
            transition=transition,
            entity_version="1",
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "status": _map_state_to_status(response.metadata.state),
                    "message": f"Order {transition}d successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error updating order %s: %s", order_id, str(e))
        return jsonify({"error": str(e)}), 500


def _map_state_to_status(state: str) -> str:
    """Map entity state to API status"""
    state_mapping = {
        "placed": "PLACED",
        "approved": "APPROVED",
        "delivered": "DELIVERED",
        "cancelled": "CANCELLED",
    }
    return state_mapping.get(state, "UNKNOWN")
