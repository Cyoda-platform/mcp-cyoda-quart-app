"""
HnItem Routes for Cyoda Client Application

Manages all HnItem-related API endpoints including CRUD operations,
workflow transitions, and hierarchy operations.
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
from application.entity.hnitem.version_1.hnitem import HnItem
from application.models import (
    HnItemQueryParams,
    HnItemUpdateQueryParams,
    BulkCreateRequest,
    TransitionRequest,
    HierarchyQueryParams,
    HnItemResponse,
    HnItemListResponse,
    BulkCreateResponse,
    TransitionResponse,
    HierarchyResponse,
    ErrorResponse,
    ValidationErrorResponse,
    DeleteResponse,
)

# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

hnitem_bp = Blueprint("hnitem", __name__, url_prefix="/api/v1/hnitem")


@hnitem_bp.route("", methods=["POST"])
@tag(["hnitem"])
@operation_id("create_hn_item")
@validate(
    request=HnItem,
    responses={
        201: (HnItemResponse, None),
        400: (ValidationErrorResponse, None),
        409: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_hn_item(data: HnItem) -> ResponseReturnValue:
    """Create a new HN item"""
    try:
        # Check if item with same HN ID already exists
        existing_item = await _find_item_by_hn_id(data.id)
        if existing_item:
            return jsonify({
                "success": False,
                "error": {
                    "code": "ITEM_ALREADY_EXISTS",
                    "message": "HN item with this ID already exists",
                    "details": f"Item with HN ID {data.id} already exists"
                }
            }), 409

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=HnItem.ENTITY_NAME,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        logger.info("Created HnItem with ID: %s", response.metadata.id)

        # Return created entity
        return jsonify({
            "success": True,
            "data": _to_entity_dict(response.data),
            "message": "HN item created successfully"
        }), 201

    except ValueError as e:
        logger.warning("Validation error creating HnItem: %s", str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": [str(e)]
            }
        }), 400
    except Exception as e:
        logger.exception("Error creating HnItem: %s", str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("/<entity_id>", methods=["GET"])
@tag(["hnitem"])
@operation_id("get_hn_item")
@validate(
    responses={
        200: (HnItemResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_hn_item(entity_id: str) -> ResponseReturnValue:
    """Get HN item by technical ID"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HnItem.ENTITY_NAME,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        if not response:
            return jsonify({
                "success": False,
                "error": {
                    "code": "ITEM_NOT_FOUND",
                    "message": "HN item not found",
                    "details": f"No item found with technical_id: {entity_id}"
                }
            }), 404

        return jsonify({
            "success": True,
            "data": _to_entity_dict(response.data)
        }), 200

    except Exception as e:
        logger.exception("Error getting HnItem %s: %s", entity_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("/hn/<int:hn_id>", methods=["GET"])
@tag(["hnitem"])
@operation_id("get_hn_item_by_hn_id")
@validate(
    responses={
        200: (HnItemResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_hn_item_by_hn_id(hn_id: int) -> ResponseReturnValue:
    """Get HN item by original Hacker News ID"""
    try:
        item = await _find_item_by_hn_id(hn_id)
        
        if not item:
            return jsonify({
                "success": False,
                "error": {
                    "code": "ITEM_NOT_FOUND",
                    "message": "HN item not found",
                    "details": f"No item found with HN ID: {hn_id}"
                }
            }), 404

        return jsonify({
            "success": True,
            "data": _to_entity_dict(item.data)
        }), 200

    except Exception as e:
        logger.exception("Error getting HnItem by HN ID %s: %s", hn_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(HnItemUpdateQueryParams)
@tag(["hnitem"])
@operation_id("update_hn_item")
@validate(
    request=HnItem,
    responses={
        200: (HnItemResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_hn_item(
    entity_id: str, data: HnItem, query_args: HnItemUpdateQueryParams
) -> ResponseReturnValue:
    """Update HN item and optionally trigger workflow transition"""
    try:
        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=HnItem.ENTITY_NAME,
            transition=transition,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        logger.info("Updated HnItem %s", entity_id)

        message = "HN item updated successfully"
        if transition:
            message += f" and transition '{transition}' triggered"

        return jsonify({
            "success": True,
            "data": _to_entity_dict(response.data),
            "message": message
        }), 200

    except ValueError as e:
        logger.warning("Validation error updating HnItem %s: %s", entity_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": [str(e)]
            }
        }), 400
    except Exception as e:
        logger.exception("Error updating HnItem %s: %s", entity_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("", methods=["GET"])
@validate_querystring(HnItemQueryParams)
@tag(["hnitem"])
@operation_id("list_hn_items")
@validate(
    responses={
        200: (HnItemListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_hn_items(query_args: HnItemQueryParams) -> ResponseReturnValue:
    """List HN items with optional filtering and pagination"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.type:
            search_conditions["type"] = query_args.type
        if query_args.by:
            search_conditions["by"] = query_args.by
        if query_args.source:
            search_conditions["source"] = query_args.source
        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=HnItem.ENTITY_NAME,
                condition=condition,
                entity_version=str(HnItem.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=HnItem.ENTITY_NAME,
                entity_version=str(HnItem.ENTITY_VERSION),
            )

        # Convert to list
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        total = len(entity_list)
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({
            "success": True,
            "data": {
                "items": paginated_entities,
                "pagination": {
                    "total": total,
                    "limit": query_args.limit,
                    "offset": query_args.offset,
                    "has_next": end < total,
                    "has_prev": start > 0
                }
            }
        }), 200

    except Exception as e:
        logger.exception("Error listing HnItems: %s", str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["hnitem"])
@operation_id("delete_hn_item")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_hn_item(entity_id: str) -> ResponseReturnValue:
    """Delete HN item (soft delete)"""
    try:
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=HnItem.ENTITY_NAME,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        logger.info("Deleted HnItem %s", entity_id)

        return jsonify({
            "success": True,
            "message": "HN item deleted successfully"
        }), 200

    except Exception as e:
        logger.exception("Error deleting HnItem %s: %s", entity_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@hnitem_bp.route("/<entity_id>/transition", methods=["POST"])
@tag(["hnitem"])
@operation_id("trigger_hn_item_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        422: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_transition(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HnItem.ENTITY_NAME,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({
                "success": False,
                "error": {
                    "code": "ITEM_NOT_FOUND",
                    "message": "HN item not found"
                }
            }), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition,
            entity_class=HnItem.ENTITY_NAME,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        logger.info("Executed transition '%s' on HnItem %s", data.transition, entity_id)

        return jsonify({
            "success": True,
            "data": {
                "technical_id": response.metadata.id,
                "previous_state": previous_state,
                "current_state": response.metadata.state,
                "transition": data.transition,
                "triggered_at": response.metadata.updated_at
            },
            "message": f"Transition '{data.transition}' triggered successfully"
        }), 200

    except Exception as e:
        logger.exception("Error executing transition on HnItem %s: %s", entity_id, str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "WORKFLOW_TRANSITION_ERROR",
                "message": str(e)
            }
        }), 422


@hnitem_bp.route("/bulk", methods=["POST"])
@tag(["hnitem"])
@operation_id("bulk_create_hn_items")
@validate(
    request=BulkCreateRequest,
    responses={
        201: (BulkCreateResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def bulk_create_hn_items(data: BulkCreateRequest) -> ResponseReturnValue:
    """Create multiple HN items in a single request"""
    try:
        created_items = []
        failed_count = 0

        for item_data in data.items:
            try:
                # Create HnItem instance for validation
                hn_item = HnItem(**item_data)

                # Check for duplicates
                existing_item = await _find_item_by_hn_id(hn_item.id)
                if existing_item:
                    created_items.append({
                        "technical_id": None,
                        "id": hn_item.id,
                        "status": "failed",
                        "error": "Item already exists"
                    })
                    failed_count += 1
                    continue

                # Save the entity
                entity_data = hn_item.model_dump(by_alias=True)
                response = await service.save(
                    entity=entity_data,
                    entity_class=HnItem.ENTITY_NAME,
                    entity_version=str(HnItem.ENTITY_VERSION),
                )

                created_items.append({
                    "technical_id": response.metadata.id,
                    "id": hn_item.id,
                    "status": "created"
                })

                # Auto-validate if requested
                if data.auto_validate:
                    try:
                        await service.execute_transition(
                            entity_id=response.metadata.id,
                            transition="validate_item",
                            entity_class=HnItem.ENTITY_NAME,
                            entity_version=str(HnItem.ENTITY_VERSION),
                        )
                    except Exception as e:
                        logger.warning(f"Auto-validation failed for item {hn_item.id}: {str(e)}")

            except Exception as e:
                created_items.append({
                    "technical_id": None,
                    "id": item_data.get("id", "unknown"),
                    "status": "failed",
                    "error": str(e)
                })
                failed_count += 1

        successful_count = len(data.items) - failed_count

        return jsonify({
            "success": True,
            "data": {
                "created_items": created_items,
                "summary": {
                    "total_requested": len(data.items),
                    "successfully_created": successful_count,
                    "failed": failed_count
                }
            },
            "message": "Bulk creation completed successfully"
        }), 201

    except Exception as e:
        logger.exception("Error in bulk create: %s", str(e))
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


async def _find_item_by_hn_id(hn_id: int) -> Any:
    """Find item by HN ID"""
    try:
        builder = SearchConditionRequest.builder()
        builder.equals("id", str(hn_id))
        condition = builder.build()

        results = await service.search(
            entity_class=HnItem.ENTITY_NAME,
            condition=condition,
            entity_version=str(HnItem.ENTITY_VERSION),
        )

        return results[0] if results else None

    except Exception as e:
        logger.warning(f"Error finding item by HN ID {hn_id}: {str(e)}")
        return None
