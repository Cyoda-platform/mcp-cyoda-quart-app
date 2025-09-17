"""
HNItemCollection Routes for Cyoda Client Application

Manages all HNItemCollection-related API endpoints including bulk operations
and Firebase API integration as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import tag

from application.entity.hnitemcollection.version_1.hnitemcollection import HNItemCollection
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

hnitemcollection_bp = Blueprint("hnitemcollection", __name__, url_prefix="/api/hnitemcollection")

@hnitemcollection_bp.route("", methods=["POST"])
@tag(["hnitemcollection"])
async def create_collection() -> ResponseReturnValue:
    """Create a new HN item collection"""
    try:
        data = await request.get_json()
        
        # Extract transition if provided
        transition = data.get("transition")
        collection_data = data.get("data", data)
        
        # Create HNItemCollection instance for validation
        collection = HNItemCollection(**collection_data)
        
        # Convert to dict for entity service
        entity_data = collection.model_dump(by_alias=True)
        
        # Get entity service
        service = get_entity_service()
        
        # Save the entity
        if transition:
            response = await service.save(
                entity=entity_data,
                entity_class=HNItemCollection.ENTITY_NAME,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
                transition=transition
            )
        else:
            response = await service.save(
                entity=entity_data,
                entity_class=HNItemCollection.ENTITY_NAME,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
            )
        
        logger.info("Created HNItemCollection with ID: %s", response.metadata.id)
        
        return jsonify({
            "id": response.metadata.id,
            "status": "success"
        }), 201
        
    except ValueError as e:
        logger.warning("Validation error creating HNItemCollection: %s", str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error creating HNItemCollection: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitemcollection_bp.route("/bulk-upload", methods=["POST"])
@tag(["hnitemcollection"])
async def bulk_upload() -> ResponseReturnValue:
    """Upload HN items from JSON file/data"""
    try:
        data = await request.get_json()
        
        collection_name = data.get("collection_name", "Bulk Upload Collection")
        items = data.get("items", [])
        
        if not items:
            return jsonify({"error": "No items provided", "code": "EMPTY_REQUEST"}), 400
        
        # Create collection for bulk upload
        collection = HNItemCollection(
            name=collection_name,
            source="bulk_upload",
            items=items,
            total_items=len(items)
        )
        
        # Add metadata about the upload
        collection.metadata = {
            "upload_type": "bulk_json",
            "original_item_count": len(items)
        }
        
        # Convert to dict for entity service
        entity_data = collection.model_dump(by_alias=True)
        
        service = get_entity_service()
        
        # Save the collection
        response = await service.save(
            entity=entity_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )
        
        logger.info("Created bulk upload collection with ID: %s", response.metadata.id)
        
        return jsonify({
            "collection_id": response.metadata.id,
            "status": "success",
            "items_count": len(items),
            "message": "Bulk upload collection created. Use begin_processing transition to start processing."
        }), 201
        
    except Exception as e:
        logger.exception("Error creating bulk upload collection: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitemcollection_bp.route("/firebase-pull", methods=["POST"])
@tag(["hnitemcollection"])
async def firebase_pull() -> ResponseReturnValue:
    """Trigger Firebase HN API pull"""
    try:
        data = await request.get_json()
        
        collection_name = data.get("collection_name", "Firebase API Pull")
        api_endpoint = data.get("api_endpoint", "topstories")
        limit = data.get("limit", 50)
        
        # Validate API endpoint
        valid_endpoints = ["topstories", "newstories", "beststories", "askstories", "showstories", "jobstories"]
        if api_endpoint not in valid_endpoints:
            return jsonify({
                "error": f"Invalid API endpoint. Must be one of: {valid_endpoints}",
                "code": "INVALID_ENDPOINT"
            }), 400
        
        # Create collection for Firebase pull
        collection = HNItemCollection(
            name=collection_name,
            source="firebase_api"
        )
        
        # Add metadata about the Firebase pull
        collection.metadata = {
            "api_endpoint": api_endpoint,
            "limit": limit,
            "pull_type": "firebase_api"
        }
        
        # Convert to dict for entity service
        entity_data = collection.model_dump(by_alias=True)
        
        service = get_entity_service()
        
        # Save the collection
        response = await service.save(
            entity=entity_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )
        
        logger.info("Created Firebase pull collection with ID: %s", response.metadata.id)
        
        return jsonify({
            "collection_id": response.metadata.id,
            "status": "success",
            "api_endpoint": api_endpoint,
            "limit": limit,
            "message": "Firebase pull collection created. Use begin_processing transition to start fetching."
        }), 201
        
    except Exception as e:
        logger.exception("Error creating Firebase pull collection: %s", str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitemcollection_bp.route("/<entity_id>", methods=["GET"])
@tag(["hnitemcollection"])
async def get_collection_status(entity_id: str) -> ResponseReturnValue:
    """Get collection status and results"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        
        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )
        
        if not response:
            return jsonify({"error": "HNItemCollection not found", "code": "NOT_FOUND"}), 404
        
        # Get collection data
        collection_data = _to_entity_dict(response.data)
        
        # Return the collection data with metadata and processing summary
        result = {
            "id": response.metadata.id,
            "data": collection_data,
            "meta": {
                "state": response.metadata.state,
                "created_at": response.metadata.created_at,
                "updated_at": response.metadata.updated_at
            },
            "processing_summary": {
                "total_items": collection_data.get("totalItems", 0),
                "processed_items": collection_data.get("processedItems", 0),
                "failed_items": collection_data.get("failedItems", 0),
                "success_rate": collection_data.get("processedItems", 0) / max(collection_data.get("totalItems", 1), 1),
                "is_complete": (collection_data.get("processedItems", 0) + collection_data.get("failedItems", 0)) >= collection_data.get("totalItems", 0)
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.exception("Error getting HNItemCollection %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitemcollection_bp.route("/<entity_id>", methods=["PUT"])
@tag(["hnitemcollection"])
async def update_collection(entity_id: str) -> ResponseReturnValue:
    """Update collection and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        
        data = await request.get_json()
        transition = request.args.get("transition")
        
        # Create HNItemCollection instance for validation
        collection = HNItemCollection(**data)
        
        # Convert to dict for entity service
        entity_data = collection.model_dump(by_alias=True)
        
        service = get_entity_service()
        
        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            transition=transition,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )
        
        logger.info("Updated HNItemCollection %s", entity_id)
        
        return jsonify(_to_entity_dict(response.data)), 200
        
    except Exception as e:
        logger.exception("Error updating HNItemCollection %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500

@hnitemcollection_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["hnitemcollection"])
async def trigger_transition(entity_id: str) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        data = await request.get_json()
        transition_name = data.get("transition_name")
        
        if not transition_name:
            return jsonify({"error": "Transition name is required", "code": "MISSING_TRANSITION"}), 400
        
        service = get_entity_service()
        
        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=transition_name,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )
        
        logger.info("Executed transition '%s' on HNItemCollection %s", transition_name, entity_id)
        
        return jsonify({
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "transition": transition_name,
            "new_state": response.metadata.state
        }), 200
        
    except Exception as e:
        logger.exception("Error executing transition on HNItemCollection %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500
