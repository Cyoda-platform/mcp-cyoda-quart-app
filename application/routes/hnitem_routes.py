"""
HNItem Routes for Cyoda Client Application

Manages all HNItem-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import tag, validate

from common.service.entity_service import SearchConditionRequest
from application.entity.hnitem.version_1.hnitem import HNItem
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

hnitem_bp = Blueprint("hnitem", __name__, url_prefix="/api/hnitem")

@hnitem_bp.route("", methods=["POST"])
@tag(["hnitem"])
async def create_hnitem() -> ResponseReturnValue:
    """Create a single HN item"""
    try:
        data = await request.get_json()
        
        # Extract transition if provided
        transition = data.get("transition")
        item_data = data.get("data", data)
        
        # Create HNItem instance for validation
        hn_item = HNItem(**item_data)
        
        # Convert to dict for entity service
        entity_data = hn_item.model_dump(by_alias=True)
        
        # Get entity service
        service = get_entity_service()
        
        # Save the entity
        if transition:
            response = await service.save(
                entity=entity_data,
                entity_class=HNItem.ENTITY_NAME,
                entity_version=str(HNItem.ENTITY_VERSION),
                transition=transition
            )
        else:
            response = await service.save(
                entity=entity_data,
                entity_class=HNItem.ENTITY_NAME,
                entity_version=str(HNItem.ENTITY_VERSION),
            )
        
        logger.info("Created HNItem with ID: %s", response.metadata.id)
        
        return jsonify({
            "id": response.metadata.id,
            "status": "success"
        }), 201
        
    except ValueError as e:
        logger.warning("Validation error creating HNItem: %s", str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error creating HNItem: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitem_bp.route("/bulk", methods=["POST"])
@tag(["hnitem"])
async def create_bulk_hnitems() -> ResponseReturnValue:
    """Create multiple HN items"""
    try:
        data = await request.get_json()
        items = data.get("items", [])
        
        if not items:
            return jsonify({"error": "No items provided", "code": "EMPTY_REQUEST"}), 400
        
        service = get_entity_service()
        created_items = []
        failed_items = []
        
        for item_data in items:
            try:
                # Create HNItem instance for validation
                hn_item = HNItem(**item_data)
                
                # Convert to dict for entity service
                entity_data = hn_item.model_dump(by_alias=True)
                
                # Save the entity
                response = await service.save(
                    entity=entity_data,
                    entity_class=HNItem.ENTITY_NAME,
                    entity_version=str(HNItem.ENTITY_VERSION),
                )
                
                created_items.append({
                    "id": response.metadata.id,
                    "hn_id": item_data.get("id")
                })
                
            except Exception as item_error:
                logger.error("Error creating item %s: %s", item_data.get("id", "unknown"), str(item_error))
                failed_items.append({
                    "hn_id": item_data.get("id", "unknown"),
                    "error": str(item_error)
                })
        
        return jsonify({
            "created": len(created_items),
            "failed": len(failed_items),
            "created_items": created_items,
            "failed_items": failed_items
        }), 201
        
    except Exception as e:
        logger.exception("Error creating bulk HNItems: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitem_bp.route("/<entity_id>", methods=["GET"])
@tag(["hnitem"])
async def get_hnitem(entity_id: str) -> ResponseReturnValue:
    """Get HN item by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        
        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItem.ENTITY_NAME,
            entity_version=str(HNItem.ENTITY_VERSION),
        )
        
        if not response:
            return jsonify({"error": "HNItem not found", "code": "NOT_FOUND"}), 404
        
        # Return the entity data with metadata
        result = {
            "id": response.metadata.id,
            "data": _to_entity_dict(response.data),
            "meta": {
                "state": response.metadata.state,
                "created_at": response.metadata.created_at,
                "updated_at": response.metadata.updated_at
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.exception("Error getting HNItem %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitem_bp.route("/search", methods=["GET"])
@tag(["hnitem"])
async def search_hnitems() -> ResponseReturnValue:
    """Search HN items with query parameters"""
    try:
        # Get query parameters
        query_text = request.args.get("q", "")
        item_type = request.args.get("type")
        author = request.args.get("author")
        include_children = request.args.get("include_children", "false").lower() == "true"
        limit = int(request.args.get("limit", "50"))
        offset = int(request.args.get("offset", "0"))
        
        service = get_entity_service()
        
        # Build search conditions
        builder = SearchConditionRequest.builder()
        
        if item_type:
            builder.equals("type", item_type)
        
        if author:
            builder.equals("by", author)
        
        # For text search, we'll search in multiple fields
        # This is a simplified implementation
        if query_text:
            # In a real implementation, you'd use full-text search
            # For now, we'll search by title containing the query
            builder.contains("title", query_text)
        
        search_request = builder.build()
        results = await service.search(
            entity_class=HNItem.ENTITY_NAME,
            condition=search_request,
            entity_version=str(HNItem.ENTITY_VERSION),
        )
        
        # Process results
        processed_results = []
        for result in results[offset:offset + limit]:
            item_data = _to_entity_dict(result.data)
            
            result_entry = {
                "item_id": result.metadata.id,
                "data": item_data
            }
            
            # Include children if requested
            if include_children and item_data.get("kids"):
                result_entry["children_count"] = len(item_data.get("kids", []))
            
            processed_results.append(result_entry)
        
        return jsonify({
            "results": processed_results,
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "query": {
                "text": query_text,
                "type": item_type,
                "author": author,
                "include_children": include_children
            }
        }), 200
        
    except Exception as e:
        logger.exception("Error searching HNItems: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitem_bp.route("/<entity_id>", methods=["PUT"])
@tag(["hnitem"])
async def update_hnitem(entity_id: str) -> ResponseReturnValue:
    """Update HN item and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        
        data = await request.get_json()
        transition = request.args.get("transition")
        
        # Create HNItem instance for validation
        hn_item = HNItem(**data)
        
        # Convert to dict for entity service
        entity_data = hn_item.model_dump(by_alias=True)
        
        service = get_entity_service()
        
        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=HNItem.ENTITY_NAME,
            transition=transition,
            entity_version=str(HNItem.ENTITY_VERSION),
        )
        
        logger.info("Updated HNItem %s", entity_id)
        
        return jsonify(_to_entity_dict(response.data)), 200
        
    except Exception as e:
        logger.exception("Error updating HNItem %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitem_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["hnitem"])
async def delete_hnitem(entity_id: str) -> ResponseReturnValue:
    """Delete HN item"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        
        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=HNItem.ENTITY_NAME,
            entity_version=str(HNItem.ENTITY_VERSION),
        )
        
        logger.info("Deleted HNItem %s", entity_id)
        
        return jsonify({
            "success": True,
            "message": "HNItem deleted successfully",
            "entity_id": entity_id
        }), 200
        
    except Exception as e:
        logger.exception("Error deleting HNItem %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500
