"""
Store Routes for Product Performance Analysis and Reporting System

Manages all Store-related API endpoints including CRUD operations
and workflow transitions following the thin proxy pattern.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring
from pydantic import BaseModel, Field

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service
from application.entity.store.version_1.store import Store


# Request/Response models
class StoreQueryParams(BaseModel):
    """Query parameters for listing stores"""
    store_name: Optional[str] = Field(None, description="Filter by store name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class StoreUpdateQueryParams(BaseModel):
    """Query parameters for updating stores"""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class DeleteResponse(BaseModel):
    """Delete response model"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


stores_bp = Blueprint("stores", __name__, url_prefix="/api/stores")


@stores_bp.route("", methods=["POST"])
@tag(["stores"])
@operation_id("create_store")
@validate(
    request=Store,
    responses={
        201: (Store, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_store(data: Store) -> ResponseReturnValue:
    """Create a new Store entity"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )

        logger.info("Created Store with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Store: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Store: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@stores_bp.route("/<entity_id>", methods=["GET"])
@tag(["stores"])
@operation_id("get_store")
@validate(
    responses={
        200: (Store, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_store(entity_id: str) -> ResponseReturnValue:
    """Get Store by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Store not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@stores_bp.route("", methods=["GET"])
@validate_querystring(StoreQueryParams)
@tag(["stores"])
@operation_id("list_stores")
@validate(
    responses={
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_stores(query_args: StoreQueryParams) -> ResponseReturnValue:
    """List Stores with optional filtering"""
    try:
        service = get_entity_service()
        
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.store_name:
            search_conditions["storeName"] = query_args.store_name

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Store.ENTITY_NAME,
                condition=condition,
                entity_version=str(Store.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Store.ENTITY_NAME,
                entity_version=str(Store.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"stores": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Stores: %s", str(e))
        return {"error": str(e)}, 500


@stores_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(StoreUpdateQueryParams)
@tag(["stores"])
@operation_id("update_store")
@validate(
    request=Store,
    responses={
        200: (Store, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_store(
    entity_id: str, data: Store, query_args: StoreUpdateQueryParams
) -> ResponseReturnValue:
    """Update Store and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Store.ENTITY_NAME,
            transition=transition,
            entity_version=str(Store.ENTITY_VERSION),
        )

        logger.info("Updated Store %s", entity_id)

        # Return updated entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@stores_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["stores"])
@operation_id("delete_store")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_store(entity_id: str) -> ResponseReturnValue:
    """Delete Store"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )

        logger.info("Deleted Store %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Store deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@stores_bp.route("/<entity_id>/sync-inventory", methods=["POST"])
@tag(["stores"])
@operation_id("sync_store_inventory")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def sync_store_inventory(entity_id: str) -> ResponseReturnValue:
    """Trigger inventory synchronization for a specific store"""
    try:
        service = get_entity_service()
        
        # Trigger the sync_inventory transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="sync_inventory",
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )

        logger.info("Triggered inventory sync for Store %s", entity_id)

        return {
            "message": "Inventory synchronization triggered successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error syncing inventory for Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "SYNC_ERROR"}, 500
