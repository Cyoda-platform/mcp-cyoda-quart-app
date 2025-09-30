"""
Product Routes for Pet Store Performance Analysis System

Manages all Product-related API endpoints including CRUD operations
and workflow transitions for product performance analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.product.version_1.product import Product
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Request/Response models
class ProductQueryParams(BaseModel):
    category: Optional[str] = Field(None, description="Filter by product category")
    status: Optional[str] = Field(None, description="Filter by product status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class ProductUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


class SearchRequest(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None


class DeleteResponse(BaseModel):
    success: bool
    message: str
    entity_id: str


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


# Create blueprint
products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["POST"])
@tag(["products"])
@operation_id("create_product")
@validate(
    request=Product,
    responses={
        201: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_product(data: Product) -> ResponseReturnValue:
    """Create a new Product entity"""
    try:
        entity_data = data.model_dump(by_alias=True)

        entity_service = get_entity_service()
        response = await entity_service.save(
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
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_product(entity_id: str) -> ResponseReturnValue:
    """Get Product by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        response = await entity_service.get_by_id(
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
@validate_querystring(ProductQueryParams)
@tag(["products"])
@operation_id("list_products")
@validate(
    responses={
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_products(query_args: ProductQueryParams) -> ResponseReturnValue:
    """List Products with optional filtering"""
    try:
        entity_service = get_entity_service()
        search_conditions: Dict[str, str] = {}

        if query_args.category:
            search_conditions["category"] = query_args.category
        if query_args.status:
            search_conditions["status"] = query_args.status
        if query_args.state:
            search_conditions["state"] = query_args.state

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )
        else:
            entities = await entity_service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Products: %s", str(e))
        return {"error": str(e)}, 500


@products_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(ProductUpdateQueryParams)
@tag(["products"])
@operation_id("update_product")
@validate(
    request=Product,
    responses={
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_product(
    entity_id: str, data: Product, query_args: ProductUpdateQueryParams
) -> ResponseReturnValue:
    """Update Product and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await entity_service.update(
            entity_id=entity_id,
            entity=entity_data,
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
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_product(entity_id: str) -> ResponseReturnValue:
    """Delete Product"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        await entity_service.delete_by_id(
            entity_id=entity_id,
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )

        logger.info("Deleted Product %s", entity_id)

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


@products_bp.route("/search", methods=["POST"])
@tag(["products"])
@operation_id("search_products")
@validate(
    request=SearchRequest,
    responses={
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_products(data: SearchRequest) -> ResponseReturnValue:
    """Search Products using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        entity_service = get_entity_service()
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(
            entity_class=Product.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Product.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Products: %s", str(e))
        return {"error": str(e)}, 500
