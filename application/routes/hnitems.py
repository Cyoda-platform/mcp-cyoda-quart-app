"""
HNItem Routes for Cyoda Client Application

Manages all HNItem-related API endpoints including CRUD operations,
bulk operations, and Firebase API integration as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.hnitem.version_1.hnitem import HNItem
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Request/Response Models
class HNItemQueryParams(BaseModel):
    """Query parameters for listing HNItems"""

    type: Optional[str] = Field(None, description="Filter by item type")
    by: Optional[str] = Field(None, description="Filter by author")
    parent: Optional[int] = Field(None, description="Filter by parent ID")
    limit: int = Field(10, description="Number of items to return", ge=1, le=100)
    offset: int = Field(0, description="Number of items to skip", ge=0)


class HNItemUpdateQueryParams(BaseModel):
    """Query parameters for updating HNItems"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class HNItemSearchParams(BaseModel):
    """Query parameters for searching HNItems"""

    q: str = Field(..., description="Search query text")
    type: Optional[str] = Field(None, description="Filter by item type")
    by: Optional[str] = Field(None, description="Filter by author")
    parent: Optional[int] = Field(None, description="Filter by parent ID")
    limit: int = Field(10, description="Number of results to return", ge=1, le=100)
    offset: int = Field(0, description="Number of results to skip", ge=0)
    include_hierarchy: bool = Field(False, description="Include parent hierarchy")


class HNItemArrayRequest(BaseModel):
    """Request model for array of HNItems"""

    items: List[Dict[str, Any]] = Field(..., description="Array of HN item data")
    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class HNItemBulkRequest(BaseModel):
    """Request model for bulk HNItem upload"""

    data: List[Dict[str, Any]] = Field(..., description="Bulk HN item data")
    source: Optional[str] = Field(None, description="Source description")
    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class FirebasePullRequest(BaseModel):
    """Request model for Firebase API pull"""

    endpoint: Optional[str] = Field(None, description="Firebase API endpoint")
    filters: Optional[Dict[str, Any]] = Field(None, description="API filters")
    limit: Optional[int] = Field(100, description="Number of items to pull")


class HNItemResponse(BaseModel):
    """Response model for single HNItem"""

    id: str = Field(..., description="Entity ID")
    status: str = Field(..., description="Operation status")
    transition: Optional[str] = Field(None, description="Applied transition")


class HNItemListResponse(BaseModel):
    """Response model for HNItem list"""

    items: List[Dict[str, Any]] = Field(..., description="List of HN items")
    total: int = Field(..., description="Total number of items")


class HNItemSearchResponse(BaseModel):
    """Response model for HNItem search"""

    items: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Search query")
    execution_time_ms: Optional[int] = Field(None, description="Query execution time")


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


hnitems_bp = Blueprint("hnitems", __name__, url_prefix="/hnitem")


# ---- Core CRUD Routes -------------------------------------------------------


@hnitems_bp.route("", methods=["POST"])
@tag(["hnitems"])
@operation_id("create_hnitem")
@validate(
    request=HNItem,
    responses={
        201: (HNItemResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def create_hnitem(data: HNItem) -> ResponseReturnValue:
    """Create a single HN item"""
    try:
        # Get optional transition from query params
        transition = request.args.get("transition")

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True, exclude_none=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=HNItem.ENTITY_NAME,
            entity_version=str(HNItem.ENTITY_VERSION),
        )

        # Apply transition if specified
        if transition:
            await service.execute_transition(
                entity_id=response.metadata.id,
                transition=transition,
                entity_class=HNItem.ENTITY_NAME,
                entity_version=str(HNItem.ENTITY_VERSION),
            )

        logger.info("Created HNItem with ID: %s", response.metadata.id)

        return {
            "id": response.metadata.id,
            "status": "created",
            "transition": transition,
        }, 201

    except ValueError as e:
        logger.warning("Validation error creating HNItem: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating HNItem: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("/array", methods=["POST"])
@tag(["hnitems"])
@operation_id("create_hnitem_array")
@validate(
    request=HNItemArrayRequest,
    responses={
        201: (Dict[str, Any], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def create_hnitem_array(data: HNItemArrayRequest) -> ResponseReturnValue:
    """Create multiple HN items from array"""
    try:
        created_items = []
        failed_items = []

        for item_data in data.items:
            try:
                # Create HNItem from data
                hn_item = HNItem(**item_data)
                entity_data = hn_item.model_dump(by_alias=True, exclude_none=True)

                # Save the entity
                response = await service.save(
                    entity=entity_data,
                    entity_class=HNItem.ENTITY_NAME,
                    entity_version=str(HNItem.ENTITY_VERSION),
                )

                # Apply transition if specified
                if data.transition:
                    await service.execute_transition(
                        entity_id=response.metadata.id,
                        transition=data.transition,
                        entity_class=HNItem.ENTITY_NAME,
                        entity_version=str(HNItem.ENTITY_VERSION),
                    )

                created_items.append(
                    {
                        "id": response.metadata.id,
                        "hn_id": item_data.get("id"),
                        "status": "created",
                    }
                )

            except Exception as e:
                failed_items.append({"hn_id": item_data.get("id"), "error": str(e)})

        logger.info(
            "Created %d HNItems, %d failed", len(created_items), len(failed_items)
        )

        return {
            "created": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items),
            "transition": data.transition,
        }, 201

    except Exception as e:
        logger.exception("Error creating HNItem array: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("/bulk", methods=["POST"])
@tag(["hnitems"])
@operation_id("create_hnitem_bulk")
@validate(
    request=HNItemBulkRequest,
    responses={
        201: (Dict[str, Any], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def create_hnitem_bulk(data: HNItemBulkRequest) -> ResponseReturnValue:
    """Bulk upload HN items from JSON data"""
    try:
        from application.entity.hnitemcollection.version_1.hnitemcollection import (
            HNItemCollection,
        )

        # Create HNItemCollection for bulk processing
        collection = HNItemCollection(
            collection_type="array",
            source=data.source or "bulk_upload",
            total_items=len(data.data),
            items=data.data,
        )

        collection_data = collection.model_dump(by_alias=True, exclude_none=True)

        # Save the collection
        response = await service.save(
            entity=collection_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        # Apply transition if specified
        if data.transition:
            await service.execute_transition(
                entity_id=response.metadata.id,
                transition=data.transition,
                entity_class=HNItemCollection.ENTITY_NAME,
                entity_version=str(HNItemCollection.ENTITY_VERSION),
            )

        logger.info(
            "Created HNItemCollection for bulk upload with ID: %s", response.metadata.id
        )

        return {
            "collection_id": response.metadata.id,
            "status": "created",
            "total_items": len(data.data),
            "source": data.source,
            "transition": data.transition,
        }, 201

    except Exception as e:
        logger.exception("Error creating bulk HNItem upload: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("/<entity_id>", methods=["GET"])
@tag(["hnitems"])
@operation_id("get_hnitem")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def get_hnitem(entity_id: str) -> ResponseReturnValue:
    """Get HNItem by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=HNItem.ENTITY_NAME,
            entity_version=str(HNItem.ENTITY_VERSION),
        )

        if not response:
            return {"error": "HNItem not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting HNItem %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("", methods=["GET"])
@validate_querystring(HNItemQueryParams)
@tag(["hnitems"])
@operation_id("list_hnitems")
@validate(
    responses={
        200: (HNItemListResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def list_hnitems(query_args: HNItemQueryParams) -> ResponseReturnValue:
    """List HNItems with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.type:
            search_conditions["type"] = query_args.type
        if query_args.by:
            search_conditions["by"] = query_args.by
        if query_args.parent:
            search_conditions["parent"] = str(query_args.parent)

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=HNItem.ENTITY_NAME,
                condition=condition,
                entity_version=str(HNItem.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=HNItem.ENTITY_NAME,
                entity_version=str(HNItem.ENTITY_VERSION),
            )

        # Convert to list
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"items": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing HNItems: %s", str(e))
        return {"error": str(e)}, 500


@hnitems_bp.route("/search", methods=["GET"])
@validate_querystring(HNItemSearchParams)
@tag(["hnitems"])
@operation_id("search_hnitems")
@validate(
    responses={
        200: (HNItemSearchResponse, None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def search_hnitems(query_args: HNItemSearchParams) -> ResponseReturnValue:
    """Search HN items with parent hierarchy joins"""
    try:
        from application.entity.searchquery.version_1.searchquery import SearchQuery

        # Create SearchQuery entity
        search_query = SearchQuery(
            query_text=query_args.q,
            filters={
                k: v
                for k, v in {
                    "type": query_args.type,
                    "by": query_args.by,
                    "parent": query_args.parent,
                }.items()
                if v is not None
            },
            include_hierarchy=query_args.include_hierarchy,
            limit=query_args.limit,
            offset=query_args.offset,
        )

        search_data = search_query.model_dump(by_alias=True, exclude_none=True)

        # Save and execute the search
        response = await service.save(
            entity=search_data,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Execute search workflow
        await service.execute_transition(
            entity_id=response.metadata.id,
            transition="execute_search",
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        # Get updated search results
        updated_response = await service.get_by_id(
            entity_id=response.metadata.id,
            entity_class=SearchQuery.ENTITY_NAME,
            entity_version=str(SearchQuery.ENTITY_VERSION),
        )

        search_result = _to_entity_dict(updated_response.data)

        return {
            "items": search_result.get("results", []),
            "total": search_result.get("result_count", 0),
            "query": query_args.q,
            "execution_time_ms": search_result.get("execution_time_ms"),
        }, 200

    except Exception as e:
        logger.exception("Error searching HNItems: %s", str(e))
        return {"error": str(e)}, 500


@hnitems_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(HNItemUpdateQueryParams)
@tag(["hnitems"])
@operation_id("update_hnitem")
@validate(
    request=HNItem,
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def update_hnitem(
    entity_id: str, data: HNItem, query_args: HNItemUpdateQueryParams
) -> ResponseReturnValue:
    """Update HNItem and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True, exclude_none=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=HNItem.ENTITY_NAME,
            transition=query_args.transition,
            entity_version=str(HNItem.ENTITY_VERSION),
        )

        logger.info("Updated HNItem %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating HNItem %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating HNItem %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["hnitems"])
@operation_id("delete_hnitem")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (Dict[str, str], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    }
)
async def delete_hnitem(entity_id: str) -> ResponseReturnValue:
    """Delete HNItem"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=HNItem.ENTITY_NAME,
            entity_version=str(HNItem.ENTITY_VERSION),
        )

        logger.info("Deleted HNItem %s", entity_id)

        return {
            "success": True,
            "message": "HNItem deleted successfully",
            "entity_id": entity_id,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting HNItem %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@hnitems_bp.route("/pull-firebase", methods=["POST"])
@tag(["hnitems"])
@operation_id("pull_firebase_hnitems")
@validate(
    request=FirebasePullRequest,
    responses={
        201: (Dict[str, Any], None),
        400: (Dict[str, str], None),
        500: (Dict[str, str], None),
    },
)
async def pull_firebase_hnitems(data: FirebasePullRequest) -> ResponseReturnValue:
    """Trigger pull from Firebase HN API"""
    try:
        from application.entity.hnitemcollection.version_1.hnitemcollection import (
            HNItemCollection,
        )

        # Create HNItemCollection for Firebase pull
        collection = HNItemCollection(
            collection_type="firebase_pull",
            source="Firebase HN API",
            firebase_endpoint=data.endpoint or "https://hacker-news.firebaseio.com/v0",
            firebase_filters=data.filters,
            total_items=data.limit or 100,
        )

        collection_data = collection.model_dump(by_alias=True, exclude_none=True)

        # Save the collection
        response = await service.save(
            entity=collection_data,
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        # Start processing
        await service.execute_transition(
            entity_id=response.metadata.id,
            transition="start_processing",
            entity_class=HNItemCollection.ENTITY_NAME,
            entity_version=str(HNItemCollection.ENTITY_VERSION),
        )

        logger.info(
            "Created Firebase pull collection with ID: %s", response.metadata.id
        )

        return {
            "collection_id": response.metadata.id,
            "status": "processing",
            "endpoint": data.endpoint,
            "limit": data.limit,
        }, 201

    except Exception as e:
        logger.exception("Error creating Firebase pull: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
