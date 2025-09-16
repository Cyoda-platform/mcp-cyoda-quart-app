"""
Category Routes for Purrfect Pets API

Manages all Category-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from services.services import get_entity_service
from application.entity.category.version_1.category import Category

logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

@categories_bp.route("", methods=["GET"])
@tag(["categories"])
@operation_id("get_categories")
async def get_categories() -> ResponseReturnValue:
    """Get all categories"""
    try:
        service = get_entity_service()
        
        entities = await service.find_all(
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        
        # Convert to response format
        categories_data = []
        for entity_response in entities:
            category_data = _to_entity_dict(entity_response.data)
            category_data["status"] = entity_response.metadata.state
            categories_data.append(category_data)
        
        return jsonify(categories_data), 200
        
    except Exception as e:
        logger.exception("Error getting categories: %s", str(e))
        return jsonify({"error": str(e)}), 500

@categories_bp.route("/<category_id>", methods=["GET"])
@tag(["categories"])
@operation_id("get_category")
async def get_category(category_id: str) -> ResponseReturnValue:
    """Get category by ID"""
    try:
        service = get_entity_service()
        
        response = await service.get_by_id(
            entity_id=category_id,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        
        if not response:
            return jsonify({"error": "Category not found"}), 404
        
        category_data = _to_entity_dict(response.data)
        category_data["status"] = response.metadata.state
        
        return jsonify(category_data), 200
        
    except Exception as e:
        logger.exception("Error getting category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 500

@categories_bp.route("", methods=["POST"])
@tag(["categories"])
@operation_id("create_category")
async def create_category() -> ResponseReturnValue:
    """Create new category"""
    try:
        service = get_entity_service()
        data = await request.get_json()
        
        # Create Category entity from request data
        category = Category(**data)
        entity_data = category.model_dump(by_alias=True)
        
        # Save the entity (will trigger automatic transition to active)
        response = await service.save(
            entity=entity_data,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        
        logger.info("Created Category with ID: %s", response.metadata.id)
        
        return jsonify({
            "id": response.metadata.id,
            "name": category.name,
            "status": response.metadata.state,
            "message": "Category created successfully"
        }), 201
        
    except ValueError as e:
        logger.warning("Validation error creating category: %s", str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error creating category: %s", str(e))
        return jsonify({"error": str(e)}), 500

@categories_bp.route("/<category_id>", methods=["PUT"])
@tag(["categories"])
@operation_id("update_category")
async def update_category(category_id: str) -> ResponseReturnValue:
    """Update category"""
    try:
        service = get_entity_service()
        data = await request.get_json()
        
        # Get transition from query parameters
        transition = request.args.get("transition")
        
        # Map transition names to workflow transition names
        transition_map = {
            "activate": "transition_to_active",
            "deactivate": "transition_to_inactive"
        }
        
        workflow_transition = None
        if transition:
            workflow_transition = transition_map.get(transition)
            if not workflow_transition:
                return jsonify({"error": f"Invalid transition: {transition}"}), 400
        
        # Create Category entity from request data for validation
        category = Category(**data)
        entity_data = category.model_dump(by_alias=True)
        
        # Update the entity
        response = await service.update(
            entity_id=category_id,
            entity=entity_data,
            entity_class=Category.ENTITY_NAME,
            transition=workflow_transition,
            entity_version=str(Category.ENTITY_VERSION),
        )
        
        logger.info("Updated Category %s", category_id)
        
        return jsonify({
            "id": response.metadata.id,
            "name": category.name,
            "status": response.metadata.state,
            "message": f"Category updated{' and ' + transition if transition else ''} successfully"
        }), 200
        
    except ValueError as e:
        logger.warning("Validation error updating category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Error updating category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 500

@categories_bp.route("/<category_id>", methods=["DELETE"])
@tag(["categories"])
@operation_id("delete_category")
async def delete_category(category_id: str) -> ResponseReturnValue:
    """Delete category"""
    try:
        service = get_entity_service()
        
        await service.delete_by_id(
            entity_id=category_id,
            entity_class=Category.ENTITY_NAME,
            entity_version=str(Category.ENTITY_VERSION),
        )
        
        logger.info("Deleted Category %s", category_id)
        
        return jsonify({
            "success": True,
            "message": "Category deleted successfully",
            "entity_id": category_id
        }), 200
        
    except Exception as e:
        logger.exception("Error deleting category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 500
