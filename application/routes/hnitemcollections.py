"""
HNItemCollection Routes for Cyoda Client Application

Manages all HNItemCollection-related API endpoints including CRUD operations
and collection-specific operations for bulk processing.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Request/Response Models
class HNItemCollectionQueryParams(BaseModel):
    """Query parameters for listing HNItemCollections"""

    collection_type: Optional[str] = Field(
        None, description="Filter by collection type"
    )
    source: Optional[str] = Field(None, description="Filter by source")
    limit: int = Field(10, description="Number of collections to return", ge=1, le=100)
    offset: int = Field(0, description="Number of collections to skip", ge=0)


class HNItemCollectionUpdateQueryParams(BaseModel):
    """Query parameters for updating HNItemCollections"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class HNItemCollectionResponse(BaseModel):
    """Response model for single HNItemCollection"""

    id: str = Field(..., description="Entity ID")
    status: str = Field(..., description="Operation status")
    transition: Optional[str] = Field(None, description="Applied transition")


class HNItemCollectionListResponse(BaseModel):
    """Response model for HNItemCollection list"""

    collections: list[Dict[str, Any]] = Field(..., description="List of collections")
    total: int = Field(..., description="Total number of collections")


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


hnitemcollections_bp = Blueprint(
    "hnitemcollections", __name__, url_prefix="/hnitemcollection"
)


# ---- Core CRUD Routes -------------------------------------------------------


@hnitemcollections_bp.route("", methods=["POST"])
@tag(["hnitemcollections"])
@operation_id("create_hnitemcollection")
@validate(
    request=HNItemCollection,
    responses={
        201: (HNItemCollectionResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def create_hnitemcollection(data: HNItemCollection) -> ResponseReturnValue:
    """Create a new HNItemCollection"""
    try:
        # Get optional transition from query params
        transition = request.args.get("transition")

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True, exclude_none=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        # Apply transition if specified
        if transition:
            await service.execute_transition(
                entity_id=response.metadata.id,
                transition=transition,
                entity_class=HNItemCollection.ENTITY_NAME,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
            )

        logger.info("Created HNItemCollection with ID: %s", response.metadata.id)

        return {
            "id": response.metadata.id,
            "status": "created",
            "transition": transition,
        }, 201

    except ValueError as e:
        logger.warning("Validation error creating HNItemCollection: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating HNItemCollection: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitemcollections_bp.route("/<entity_id>", methods=["GET"])
@tag(["hnitemcollections"])
@operation_id("get_hnitemcollection")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_hnitemcollection(entity_id: str) -> ResponseReturnValue:
    """Get HNItemCollection by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        if not response:
            return {"error": "HNItemCollection not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting HNItemCollection %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitemcollections_bp.route("", methods=["GET"])
@validate_querystring(HNItemCollectionQueryParams)
@tag(["hnitemcollections"])
@operation_id("list_hnitemcollections")
@validate(
    responses={
        200: (HNItemCollectionListResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def list_hnitemcollections(
    query_args: HNItemCollectionQueryParams,
) -> ResponseReturnValue:
    """List HNItemCollections with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.collection_type:
            search_conditions["collection_type"] = query_args.collection_type
        if query_args.source:
            search_conditions["source"] = query_args.source

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=HNItemCollection.ENTITY_NAME,
                condition=condition,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=HNItemCollection.ENTITY_NAME,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
            )

        # Convert to list
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"collections": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing HNItemCollections: %s", str(e))
        return {"error": str(e)}, 500


@hnitemcollections_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(HNItemCollectionUpdateQueryParams)
@tag(["hnitemcollections"])
@operation_id("update_hnitemcollection")
@validate(
    request=HNItemCollection,
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def update_hnitemcollection(
    entity_id: str,
    data: HNItemCollection,
    query_args: HNItemCollectionUpdateQueryParams,
) -> ResponseReturnValue:
    """Update HNItemCollection and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True, exclude_none=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            transition=query_args.transition,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        logger.info("Updated HNItemCollection %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating HNItemCollection %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating HNItemCollection %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitemcollections_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["hnitemcollections"])
@operation_id("delete_hnitemcollection")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def delete_hnitemcollection(entity_id: str) -> ResponseReturnValue:
    """Delete HNItemCollection"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        logger.info("Deleted HNItemCollection %s", entity_id)

        return {
            "success": True,
            "message": "HNItemCollection deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting HNItemCollection %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Collection-specific Operations ------------------------------------------


@hnitemcollections_bp.route("/<entity_id>/status", methods=["GET"])
@tag(["hnitemcollections"])
@operation_id("get_hnitemcollection_status")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_hnitemcollection_status(entity_id: str) -> ResponseReturnValue:
    """Get processing status of HNItemCollection"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        if not response:
            return {"error": "HNItemCollection not found", "code": "NOT_FOUND"}, 404

        collection_data = _to_entity_dict(response.data)

        # Extract processing status
        status_info = {
            "collection_id": entity_id,
            "state": collection_data.get("state"),
            "collection_type": collection_data.get("collection_type"),
            "total_items": collection_data.get("total_items", 0),
            "processed_items": collection_data.get("processed_items", 0),
            "failed_items": collection_data.get("failed_items", 0),
            "success_rate": collection_data.get("success_rate", 0),
            "is_complete": collection_data.get("is_complete", False),
            "processing_started_at": collection_data.get("processing_started_at"),
            "completed_at": collection_data.get("completed_at"),
            "processing_duration_ms": collection_data.get("processing_duration_ms"),
            "error_count": len(collection_data.get("processing_errors", [])),
        }

        return status_info, 200

    except Exception as e:
        logger.exception(
            "Error getting HNItemCollection status %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitemcollections_bp.route("/<entity_id>/start", methods=["POST"])
@tag(["hnitemcollections"])
@operation_id("start_hnitemcollection_processing")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def start_hnitemcollection_processing(entity_id: str) -> ResponseReturnValue:
    """Start processing of HNItemCollection"""
    try:
        # Execute start_processing transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="start_processing",
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        logger.info("Started processing for HNItemCollection %s", entity_id)

        return {
            "collection_id": entity_id,
            "status": "processing_started",
            "state": (
                response.metadata.state if hasattr(response.metadata, "state") else None
            ),
        }, 200

    except Exception as e:
        logger.exception(
            "Error starting HNItemCollection processing %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitemcollections_bp.route("/<entity_id>/errors", methods=["GET"])
@tag(["hnitemcollections"])
@operation_id("get_hnitemcollection_errors")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_hnitemcollection_errors(entity_id: str) -> ResponseReturnValue:
    """Get processing errors for HNItemCollection"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        if not response:
            return {"error": "HNItemCollection not found", "code": "NOT_FOUND"}, 404

        collection_data = _to_entity_dict(response.data)
        processing_errors = collection_data.get("processing_errors", [])

        return {
            "collection_id": entity_id,
            "error_count": len(processing_errors),
            "errors": processing_errors,
        }, 200

    except Exception as e:
        logger.exception(
            "Error getting HNItemCollection errors %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
