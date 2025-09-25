"""
Product Routes for Pet Store Performance Analysis System

Manages all Product-related API endpoints including CRUD operations
and workflow transitions for product performance analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.product.version_1.product import Product
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["POST"])
@tag(["products"])
@operation_id("create_product")
async def create_product() -> ResponseReturnValue:
    """Create a new Product entity"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Create Product entity from request data
        product = Product(**data)
        entity_data = product.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Created Product with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Product: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Product: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@products_bp.route("/<entity_id>", methods=["GET"])
@tag(["products"])
@operation_id("get_product")
async def get_product(entity_id: str) -> ResponseReturnValue:
    """Get Product by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Product not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@products_bp.route("", methods=["GET"])
@tag(["products"])
@operation_id("list_products")
async def list_products() -> ResponseReturnValue:
    """List Products with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get("category")
        status = request.args.get("status")
        min_performance = request.args.get("min_performance")
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 50))

        service = get_entity_service()

        # Build search conditions
        search_conditions: Dict[str, str] = {}
        if category:
            search_conditions["category"] = category
        if status:
            search_conditions["status"] = status
        if min_performance:
            search_conditions["performanceScore"] = min_performance

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

        # Apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]
        paginated_entities = entity_list[offset : offset + limit]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Products: %s", str(e))
        return {"error": str(e)}, 500


@products_bp.route("/<entity_id>", methods=["PUT"])
@tag(["products"])
@operation_id("update_product")
async def update_product(entity_id: str) -> ResponseReturnValue:
    """Update Product and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_DATA"}, 400

        # Get transition from query parameters
        transition = request.args.get("transition")

        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=Product.ENTITY_NAME,
            transition=transition,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Updated Product %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@products_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["products"])
@operation_id("delete_product")
async def delete_product(entity_id: str) -> ResponseReturnValue:
    """Delete Product"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Deleted Product %s", entity_id)
        return {
            "success": True,
            "message": "Product deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@products_bp.route("/search", methods=["POST"])
@tag(["products"])
@operation_id("search_products")
async def search_products() -> ResponseReturnValue:
    """Search Products using field-value conditions"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        service = get_entity_service()
        builder = SearchConditionRequest.builder()
        for field, value in data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Product.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Product.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Products: %s", str(e))
        return {"error": str(e)}, 500


@products_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["products"])
@operation_id("trigger_product_transition")
async def trigger_transition(entity_id: str) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        data = await request.get_json()
        if not data or "transition_name" not in data:
            return {
                "error": "Transition name is required",
                "code": "MISSING_TRANSITION",
            }, 400

        service = get_entity_service()

        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "Product not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data["transition_name"],
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Product %s", data["transition_name"], entity_id
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previousState": previous_state,
            "newState": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception(
            "Error executing transition on Product %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500
