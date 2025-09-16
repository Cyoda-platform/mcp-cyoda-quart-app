"""Category routes for Purrfect Pets API."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_request, validate_querystring
from pydantic import BaseModel, Field

from service.services import get_entity_service, get_auth_service
from application.entity.category.version_1.category import Category

logger = logging.getLogger(__name__)

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

ENTITY_VERSION = "1"


class CategoryQuery(BaseModel):
    """Query parameters for category filtering."""
    page: Optional[int] = Field(0, ge=0, description="Page number")
    size: Optional[int] = Field(10, ge=1, le=100, description="Page size")
    status: Optional[str] = Field(None, description="Filter by category status")


class CategoryRequest(BaseModel):
    """Request model for creating categories."""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    imageUrl: Optional[str] = Field(None, description="Category image URL")


class CategoryUpdateRequest(BaseModel):
    """Request model for updating categories."""
    transitionName: Optional[str] = Field(None, description="Workflow transition name")
    name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    imageUrl: Optional[str] = Field(None, description="Category image URL")
    isActive: Optional[bool] = Field(None, description="Whether category is active")


def get_services():
    """Get entity service and auth service."""
    return get_entity_service(), get_auth_service()


@categories_bp.route("", methods=["GET"])
@validate_querystring(CategoryQuery)
async def get_categories():
    """Get all categories with pagination."""
    entity_service, cyoda_auth_service = get_services()
    args = CategoryQuery(**request.args)
    
    try:
        # Get all categories from entity service
        categories_response = await entity_service.find_all("Category", ENTITY_VERSION)
        categories = categories_response if categories_response else []
        
        # Apply status filter
        filtered_categories = []
        for category_data in categories:
            category = Category(**category_data) if isinstance(category_data, dict) else category_data
            
            # Apply status filter (map to state)
            if args.status:
                status_map = {
                    "ACTIVE": "active",
                    "INACTIVE": "inactive",
                    "ARCHIVED": "archived"
                }
                expected_state = status_map.get(args.status.upper())
                if expected_state and category.state != expected_state:
                    continue
                    
            filtered_categories.append(category)
        
        # Apply pagination
        total_elements = len(filtered_categories)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_categories = filtered_categories[start_idx:end_idx]
        
        # Convert to response format
        content = []
        for category in paginated_categories:
            content.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "imageUrl": category.imageUrl,
                "isActive": category.isActive,
                "state": category.state.upper() if category.state else "UNKNOWN"
            })
        
        response = {
            "content": content,
            "totalElements": total_elements
        }
        
        logger.info(f"Retrieved {len(content)} categories (page {args.page})")
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Failed to get categories: {e}")
        return jsonify({"error": f"Failed to get categories: {str(e)}"}), 500


@categories_bp.route("/<int:category_id>", methods=["GET"])
async def get_category(category_id: int):
    """Get category by ID."""
    entity_service, cyoda_auth_service = get_services()
    
    try:
        # Find category by business ID
        category_response = await entity_service.find_by_business_id(
            "Category", str(category_id), "id", ENTITY_VERSION
        )
        
        if not category_response:
            return jsonify({"error": "Category not found"}), 404
        
        category_data = category_response.entity
        category = Category(**category_data) if isinstance(category_data, dict) else category_data
        
        response = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "imageUrl": category.imageUrl,
            "isActive": category.isActive,
            "state": category.state.upper() if category.state else "UNKNOWN",
            "createdAt": category.createdAt,
            "updatedAt": category.updatedAt
        }
        
        logger.info(f"Retrieved category {category_id}")
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Failed to get category {category_id}: {e}")
        return jsonify({"error": f"Failed to get category: {str(e)}"}), 500


@categories_bp.route("", methods=["POST"])
@validate_request(CategoryRequest)
async def create_category(data: CategoryRequest):
    """Create new category."""
    entity_service, cyoda_auth_service = get_services()
    
    try:
        # Generate unique ID
        category_id = len(await entity_service.find_all("Category", ENTITY_VERSION) or []) + 1
        
        # Create category entity
        category_data = {
            "id": category_id,
            "name": data.name,
            "description": data.description,
            "imageUrl": data.imageUrl,
            "isActive": True,
            "state": "initial_state"
        }
        
        # Save category
        category_response = await entity_service.save(category_data, "Category", ENTITY_VERSION)
        
        response = {
            "id": category_id,
            "name": data.name,
            "description": data.description,
            "isActive": True,
            "state": "ACTIVE",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Created category {category_id}")
        return jsonify(response), 201

    except Exception as e:
        logger.exception(f"Failed to create category: {e}")
        return jsonify({"error": f"Failed to create category: {str(e)}"}), 500


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@validate_request(CategoryUpdateRequest)
async def update_category(category_id: int, data: CategoryUpdateRequest):
    """Update category."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing category
        category_response = await entity_service.find_by_business_id(
            "Category", str(category_id), "id", ENTITY_VERSION
        )

        if not category_response:
            return jsonify({"error": "Category not found"}), 404

        # Update fields if provided
        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.description is not None:
            update_data["description"] = data.description
        if data.imageUrl is not None:
            update_data["imageUrl"] = data.imageUrl
        if data.isActive is not None:
            update_data["isActive"] = data.isActive

        # Add timestamp
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        # Update with transition if provided
        transition = data.transitionName
        if transition:
            # Map transition names to workflow transitions
            transition_map = {
                "DEACTIVATE": "transition_to_inactive",
                "ACTIVATE": "transition_to_active",
                "ARCHIVE": "transition_to_archived"
            }
            workflow_transition = transition_map.get(transition)
        else:
            workflow_transition = None

        # Update category
        updated_response = await entity_service.update(
            category_response.metadata.id,
            update_data,
            "Category",
            workflow_transition,
            ENTITY_VERSION
        )

        # Get updated state
        updated_category_data = updated_response.entity
        updated_category = Category(**updated_category_data) if isinstance(updated_category_data, dict) else updated_category_data

        response = {
            "id": category_id,
            "name": updated_category.name,
            "isActive": updated_category.isActive,
            "state": updated_category.state.upper() if updated_category.state else "UNKNOWN",
            "updatedAt": updated_category.updatedAt
        }

        logger.info(f"Updated category {category_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to update category {category_id}: {e}")
        return jsonify({"error": f"Failed to update category: {str(e)}"}), 500


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
async def delete_category(category_id: int):
    """Delete category (archive)."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing category
        category_response = await entity_service.find_by_business_id(
            "Category", str(category_id), "id", ENTITY_VERSION
        )

        if not category_response:
            return jsonify({"error": "Category not found"}), 404

        # Archive by updating state
        delete_data = {
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }

        await entity_service.update(
            category_response.metadata.id,
            delete_data,
            "Category",
            "transition_to_archived",  # Archive transition
            ENTITY_VERSION
        )

        response = {"message": "Category deleted successfully"}

        logger.info(f"Deleted category {category_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to delete category {category_id}: {e}")
        return jsonify({"error": f"Failed to delete category: {str(e)}"}), 500
