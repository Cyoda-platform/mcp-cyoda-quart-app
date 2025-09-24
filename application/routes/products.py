"""
Product Routes for Product Performance Analysis and Reporting System

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
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class ProductUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class ProductResponse(BaseModel):
    success: bool = Field(True, description="Operation success status")
    data: Dict[str, Any] = Field(..., description="Product data")


class ProductListResponse(BaseModel):
    products: list[Dict[str, Any]] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")


class DeleteResponse(BaseModel):
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="Deleted entity ID")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    error: str = Field(..., description="Validation error message")
    code: str = Field("VALIDATION_ERROR", description="Error code")


# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


# Helper function
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


# Blueprint
products_bp = Blueprint("products", __name__, url_prefix="/api/products")


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
async def create_product(data: Product) -> ResponseReturnValue:
    """Create a new Product entity"""
    try:
        entity_data = data.model_dump(by_alias=True)

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
@validate(
    responses={
        200: (ProductResponse, None),
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
async def list_products(query_args: ProductQueryParams) -> ResponseReturnValue:
    """List Products with optional filtering"""
    try:
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

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"products": paginated_entities, "total": len(entity_list)}, 200

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
        200: (ProductResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
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

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
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

        await service.delete_by_id(
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


@products_bp.route("/count", methods=["GET"])
@tag(["products"])
@operation_id("count_products")
async def count_products() -> ResponseReturnValue:
    """Count total number of Products"""
    try:
        count = await service.count(
            entity_class=Product.ENTITY_NAME,
            entity_version=str(Product.ENTITY_VERSION),
        )
        return {"count": count}, 200
    except Exception as e:
        logger.exception("Error counting Products: %s", str(e))
        return {"error": str(e)}, 500
