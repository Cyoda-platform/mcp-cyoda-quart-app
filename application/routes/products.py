"""
Product Routes for Pet Store Performance Analysis System

Manages all Product-related API endpoints including CRUD operations
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

from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service

# Imported for entity constants / typing
from ..entity.product import Product
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ProductListResponse,
    ProductQueryParams,
    ProductResponse,
    ProductSearchResponse,
    ProductUpdateQueryParams,
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

# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

products_bp = Blueprint(
    "products", __name__, url_prefix="/api/products"
)

# ---- Routes -----------------------------------------------------------------

@products_bp.route("", methods=["POST"])
@tag(["products"])
@operation_id("create_product")
@validate(
    request=Product,
    responses={
        201: (ProductResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_product(
    data: Product,
) -> ResponseReturnValue:
    """Create a new Product with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Created Product with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
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
@validate(
    responses={
        200: (ProductResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_product(entity_id: str) -> ResponseReturnValue:
    """Get Product by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Product not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@products_bp.route("", methods=["GET"])
@validate_querystring(ProductQueryParams)
@tag(["products"])
@operation_id("list_products")
@validate(
    responses={
        200: (ProductListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_products(
    query_args: ProductQueryParams,
) -> ResponseReturnValue:
    """List Products with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.category:
            search_conditions["category"] = query_args.category

        if query_args.stock_status:
            search_conditions["stockStatus"] = query_args.stock_status

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
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

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply performance score filtering if specified
        if query_args.min_performance_score is not None or query_args.max_performance_score is not None:
            filtered_entities = []
            for entity in entity_list:
                score = entity.get("performanceScore")
                if score is not None:
                    if query_args.min_performance_score is not None and score < query_args.min_performance_score:
                        continue
                    if query_args.max_performance_score is not None and score > query_args.max_performance_score:
                        continue
                filtered_entities.append(entity)
            entity_list = filtered_entities

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Products: %s", str(e))
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(ProductUpdateQueryParams)
@tag(["products"])
@operation_id("update_product")
@validate(
    request=Product,
    responses={
        200: (ProductResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_product(
    entity_id: str, data: Product, query_args: ProductUpdateQueryParams
) -> ResponseReturnValue:
    """Update Product and optionally trigger workflow transition with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Product.ENTITY_NAME,
            transition=transition,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Updated Product %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating Product %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Product %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@products_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["products"])
@operation_id("delete_product")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_product(entity_id: str) -> ResponseReturnValue:
    """Delete Product with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Deleted Product %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Product deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Product %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Entity Service Endpoints ----------------------------------------

@products_bp.route("/by-business-id/<business_id>", methods=["GET"])
@tag(["products"])
@operation_id("get_product_by_business_id")
@validate(
    responses={
        200: (ProductResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get Product by business ID (name field by default)"""
    try:
        business_id_field = request.args.get("field", "name")  # Default to name field

        result = await service.find_by_business_id(
            entity_class=Product.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "Product not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception(
            "Error getting Product by business ID %s: %s", business_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["products"])
@operation_id("check_product_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Product exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking Product existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@products_bp.route("/count", methods=["GET"])
@tag(["products"])
@operation_id("count_products")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Products"""
    try:
        count = await service.count(
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Products: %s", str(e))
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["products"])
@operation_id("get_product_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Product"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for Product %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------

@products_bp.route("/search", methods=["POST"])
@tag(["products"])
@operation_id("search_products")
@validate(
    request=SearchRequest,
    responses={
        200: (ProductSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Products using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # KISS: Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Product.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Product.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Products: %s", str(e))
        return {"error": str(e)}, 500


@products_bp.route("/find-all", methods=["GET"])
@tag(["products"])
@operation_id("find_all_products")
@validate(
    responses={200: (ProductListResponse, None), 500: (ErrorResponse, None)}
)
async def find_all_entities() -> ResponseReturnValue:
    """Find all Products without filtering"""
    try:
        results = await service.find_all(
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding all Products: %s", str(e))
        return {"error": str(e)}, 500


@products_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["products"])
@operation_id("trigger_product_transition")
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
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Product not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Product %s",
            data.transition_name,
            entity_id,
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error executing transition on Product %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
