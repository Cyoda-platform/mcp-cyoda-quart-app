"""
UI Products Routes for Cyoda OMS Application

UI-facing REST API endpoints for product management including search and filtering
as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.product.version_1.product import Product
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)

ui_products_bp = Blueprint("ui_products", __name__, url_prefix="/ui")


@ui_products_bp.route("/products", methods=["GET"])
async def list_products() -> ResponseReturnValue:
    """
    List products with optional filtering and search.

    Query parameters:
    - search: Free-text search on name/description
    - category: Filter by category
    - minPrice: Minimum price filter
    - maxPrice: Maximum price filter
    - page: Page number (default: 0)
    - pageSize: Page size (default: 20)

    Returns slim DTO for speed: {sku, name, description, price, quantityAvailable, category, imageUrl}
    """
    try:
        # Get query parameters
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        min_price = request.args.get("minPrice")
        max_price = request.args.get("maxPrice")
        page = int(request.args.get("page", "0"))
        page_size = int(request.args.get("pageSize", "20"))

        entity_service = get_entity_service()

        # Build search conditions
        builder = SearchConditionRequest.builder()
        has_conditions = False

        # Category filter
        if category:
            builder.equals("category", category)
            has_conditions = True

        # Price range filters
        if min_price:
            try:
                min_price_val = float(min_price)
                builder.greater_or_equal("price", min_price_val)
                has_conditions = True
            except ValueError:
                return jsonify({"error": "Invalid minPrice value"}), 400

        if max_price:
            try:
                max_price_val = float(max_price)
                builder.less_or_equal("price", max_price_val)
                has_conditions = True
            except ValueError:
                return jsonify({"error": "Invalid maxPrice value"}), 400

        # Get products
        if has_conditions:
            condition = builder.build()
            products = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )
        else:
            products = await entity_service.find_all(
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

        # Convert to Product entities and apply text search
        product_list: List[Dict[str, Any]] = []
        for product_response in products:
            product_data = product_response.data
            if hasattr(product_data, "model_dump"):
                product_dict = product_data.model_dump(by_alias=True)
            else:
                product_dict = product_data

            # Apply free-text search on name/description
            if search:
                name = product_dict.get("name", "").lower()
                description = product_dict.get("description", "").lower()
                search_lower = search.lower()

                if search_lower not in name and search_lower not in description:
                    continue

            # Convert to slim DTO
            slim_product = {
                "sku": product_dict.get("sku"),
                "name": product_dict.get("name"),
                "description": product_dict.get("description"),
                "price": product_dict.get("price"),
                "quantityAvailable": product_dict.get("quantityAvailable"),
                "category": product_dict.get("category"),
                "imageUrl": _get_primary_image_url(product_dict.get("media", [])),
            }
            product_list.append(slim_product)

        # Apply pagination
        total = len(product_list)
        start = page * page_size
        end = start + page_size
        paginated_products = product_list[start:end]

        return (
            jsonify(
                {
                    "products": paginated_products,
                    "total": total,
                    "page": page,
                    "pageSize": page_size,
                    "totalPages": (total + page_size - 1) // page_size,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing products: %s", str(e))
        return jsonify({"error": str(e)}), 500


@ui_products_bp.route("/products/<sku>", methods=["GET"])
async def get_product_detail(sku: str) -> ResponseReturnValue:
    """
    Get product detail by SKU.
    Returns the full Product document (entire schema).
    """
    try:
        if not sku or len(sku.strip()) == 0:
            return jsonify({"error": "SKU is required"}), 400

        entity_service = get_entity_service()

        # Find product by SKU (business ID)
        product_response = await entity_service.find_by_business_id(
            entity_class=Product.ENTITY_NAME,
            business_id=sku,
            business_id_field="sku",
            entity_version=str(Product.ENTITY_VERSION),
        )

        if not product_response:
            return jsonify({"error": "Product not found"}), 404

        # Return full product document
        product_data = product_response.data
        if hasattr(product_data, "model_dump"):
            product_dict = product_data.model_dump(by_alias=True)
        else:
            product_dict = product_data

        return jsonify(product_dict), 200

    except Exception as e:
        logger.exception("Error getting product detail for SKU %s: %s", sku, str(e))
        return jsonify({"error": str(e)}), 500


def _get_primary_image_url(media: List[Dict[str, Any]]) -> Optional[str]:
    """Get primary image URL from media"""
    if not media:
        return None

    # Look for hero image first
    for media_item in media:
        if media_item.get("type") == "image" and "hero" in media_item.get("tags", []):
            return media_item.get("url")

    # Fallback to first image
    for media_item in media:
        if media_item.get("type") == "image":
            return media_item.get("url")

    return None
