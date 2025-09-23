"""
Product Data API Routes for Product Performance Analysis System

REST API endpoints for managing ProductData entities including CRUD operations
and data extraction triggers as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart_schema import tag, validate, validate_querystring

from application.entity.product_data.version_1.product_data import ProductData
from services.services import get_entity_service
from common.service.entity_service import SearchConditionRequest

# Create blueprint for product data routes
product_data_bp = Blueprint("product_data", __name__, url_prefix="/api/product-data")

logger = logging.getLogger(__name__)


@product_data_bp.route("/", methods=["POST"])
@tag(["ProductData"])
@validate(request=ProductData)
async def create_product_data(data: ProductData) -> tuple[Dict[str, Any], int]:
    """
    Create a new ProductData entity.

    Creates a new product data entry that will be processed through the
    data extraction and analysis workflow.
    """
    try:
        entity_service = get_entity_service()

        # Convert Pydantic model to dict for EntityService
        product_data_dict = data.model_dump(by_alias=True)

        # Save the entity using entity constants
        response = await entity_service.save(
            entity=product_data_dict,
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
        )

        # Return the created entity with technical ID and state
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": product_data_dict,
        }

        logger.info(f"Created ProductData entity with ID: {response.metadata.id}")
        return result, 201

    except Exception as e:
        logger.error(f"Error creating ProductData entity: {str(e)}")
        return {"error": "Failed to create product data", "details": str(e)}, 500


@product_data_bp.route("/<entity_id>", methods=["GET"])
@tag(["ProductData"])
async def get_product_data(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Retrieve a ProductData entity by ID.

    Returns the product data entity with current state and all extracted data.
    """
    try:
        entity_service = get_entity_service()

        # Get the entity by technical ID
        response = await entity_service.get_by_id(
            entity_id=entity_id,
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Product data not found"}, 404

        # Return the entity with metadata
        result = {
            "id": response.get_id(),
            "state": response.get_state(),
            "entity": response.data.model_dump(by_alias=True) if hasattr(response.data, 'model_dump') else response.data,
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error retrieving ProductData entity {entity_id}: {str(e)}")
        return {"error": "Failed to retrieve product data", "details": str(e)}, 500


@product_data_bp.route("/<entity_id>", methods=["PUT"])
@tag(["ProductData"])
@validate(request=ProductData)
async def update_product_data(
    entity_id: str, data: ProductData
) -> tuple[Dict[str, Any], int]:
    """
    Update a ProductData entity.

    Updates the product data and optionally triggers reprocessing through
    the analysis workflow.
    """
    try:
        entity_service = get_entity_service()

        # Get transition from query parameters (optional)
        transition = request.args.get("transition")

        # Convert Pydantic model to dict for EntityService
        product_data_dict = data.model_dump(by_alias=True)

        # Update the entity
        response = await entity_service.update(
            entity_id=entity_id,
            entity=product_data_dict,
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
            transition=transition,
        )

        # Return the updated entity
        result = {
            "id": response.get_id(),
            "state": response.get_state(),
            "entity": response.data.model_dump(by_alias=True) if hasattr(response.data, 'model_dump') else response.data,
        }

        logger.info(f"Updated ProductData entity {entity_id}")
        return result, 200

    except Exception as e:
        logger.error(f"Error updating ProductData entity {entity_id}: {str(e)}")
        return {"error": "Failed to update product data", "details": str(e)}, 500


@product_data_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["ProductData"])
async def delete_product_data(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete a ProductData entity.

    Removes the product data entity from the system.
    """
    try:
        entity_service = get_entity_service()

        # Delete the entity
        await entity_service.delete_by_id(
            entity_id=entity_id,
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
        )

        logger.info(f"Deleted ProductData entity {entity_id}")
        return {"message": "Product data deleted successfully"}, 200

    except Exception as e:
        logger.error(f"Error deleting ProductData entity {entity_id}: {str(e)}")
        return {"error": "Failed to delete product data", "details": str(e)}, 500


@product_data_bp.route("/", methods=["GET"])
@tag(["ProductData"])
async def list_product_data() -> tuple[Dict[str, Any], int]:
    """
    List ProductData entities with optional filtering.

    Returns a paginated list of product data entities with filtering options.
    """
    try:
        entity_service = get_entity_service()

        # Get query parameters
        page_size = int(request.args.get("page_size", 50))
        page_token = request.args.get("page_token")
        category = request.args.get("category")
        status = request.args.get("status")
        high_performer = request.args.get("high_performer")

        # Build search condition
        builder = SearchConditionRequest.builder()
        if category:
            builder.equals("category", category)
        if status:
            builder.equals("status", status)
        if high_performer is not None:
            builder.equals("isHighPerformer", high_performer.lower() == "true")

        # Set pagination
        if page_size:
            builder.limit(page_size)

        condition = builder.build()

        # Search for entities
        if condition.conditions:
            response = await entity_service.search(
                entity_class=ProductData.ENTITY_NAME,
                condition=condition,
                entity_version=str(ProductData.ENTITY_VERSION),
            )
        else:
            response = await entity_service.find_all(
                entity_class=ProductData.ENTITY_NAME,
                entity_version=str(ProductData.ENTITY_VERSION),
            )

        # Format response
        entities = []
        if response:
            for entity_response in response:
                entities.append({
                    "id": entity_response.get_id(),
                    "state": entity_response.get_state(),
                    "entity": entity_response.data.model_dump(by_alias=True) if hasattr(entity_response.data, 'model_dump') else entity_response.data
                })

        result = {
            "entities": entities,
            "total_count": len(entities),
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error listing ProductData entities: {str(e)}")
        return {"error": "Failed to list product data", "details": str(e)}, 500


@product_data_bp.route("/trigger-extraction", methods=["POST"])
@tag(["ProductData"])
async def trigger_data_extraction() -> tuple[Dict[str, Any], int]:
    """
    Trigger data extraction for all pending ProductData entities.

    Manually triggers the data extraction process for entities that are
    in the appropriate state for processing.
    """
    try:
        entity_service = get_entity_service()

        # Search for all entities
        response = await entity_service.find_all(
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
        )

        processed_count = 0
        if response:
            for entity_response in response:
                if entity_response.get_state() == "validated":
                    try:
                        # Trigger extraction by transitioning to data extraction
                        await entity_service.execute_transition(
                            entity_id=entity_response.get_id(),
                            transition="extract_data",
                            entity_class=ProductData.ENTITY_NAME,
                            entity_version=str(ProductData.ENTITY_VERSION),
                        )
                        processed_count += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to trigger extraction for entity {entity_response.get_id()}: {str(e)}"
                        )

        result = {
            "message": f"Triggered data extraction for {processed_count} entities",
            "processed_count": processed_count,
        }

        logger.info(
            f"Triggered data extraction for {processed_count} ProductData entities"
        )
        return result, 200

    except Exception as e:
        logger.error(f"Error triggering data extraction: {str(e)}")
        return {"error": "Failed to trigger data extraction", "details": str(e)}, 500


@product_data_bp.route("/analytics", methods=["GET"])
@tag(["ProductData"])
async def get_product_analytics() -> tuple[Dict[str, Any], int]:
    """
    Get analytics summary for all ProductData entities.

    Returns aggregated analytics including performance metrics,
    category breakdown, and inventory status.
    """
    try:
        entity_service = get_entity_service()

        # Get all product data entities
        response = await entity_service.find_all(
            entity_class=ProductData.ENTITY_NAME,
            entity_version=str(ProductData.ENTITY_VERSION),
        )

        # Initialize analytics
        analytics = {
            "total_products": 0,
            "total_revenue": 0.0,
            "total_sales_volume": 0,
            "high_performers": 0,
            "items_needing_restock": 0,
            "slow_moving_items": 0,
            "category_breakdown": {},
            "status_breakdown": {},
            "average_performance_score": 0.0,
        }

        if response:
            total_score = 0.0
            score_count = 0

            for entity_response in response:
                entity = entity_response.data.model_dump(by_alias=True) if hasattr(entity_response.data, 'model_dump') else entity_response.data
                analytics["total_products"] += 1

                # Aggregate metrics
                analytics["total_revenue"] += entity.get("revenue", 0.0)
                analytics["total_sales_volume"] += entity.get("salesVolume", 0)

                if entity.get("isHighPerformer", False):
                    analytics["high_performers"] += 1
                if entity.get("requiresRestocking", False):
                    analytics["items_needing_restock"] += 1
                if entity.get("isSlowMoving", False):
                    analytics["slow_moving_items"] += 1

                # Category breakdown
                category = entity.get("category", "Unknown")
                if category not in analytics["category_breakdown"]:
                    analytics["category_breakdown"][category] = 0
                analytics["category_breakdown"][category] += 1

                # Status breakdown
                status = entity.get("status", "Unknown")
                if status not in analytics["status_breakdown"]:
                    analytics["status_breakdown"][status] = 0
                analytics["status_breakdown"][status] += 1

                # Performance score
                score = entity.get("performanceScore")
                if score is not None:
                    total_score += score
                    score_count += 1

            # Calculate average performance score
            if score_count > 0:
                analytics["average_performance_score"] = total_score / score_count

        return analytics, 200

    except Exception as e:
        logger.error(f"Error getting product analytics: {str(e)}")
        return {"error": "Failed to get analytics", "details": str(e)}, 500
