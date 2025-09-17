"""
HNItem Routes for Cyoda Client Application

Manages all HNItem-related API endpoints including CRUD operations,
bulk operations, and Firebase API integration as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)
from pydantic import BaseModel, Field

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service
from application.entity.hnitem.version_1.hnitem import HNItem


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
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


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
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class HNItemBulkRequest(BaseModel):
    """Request model for bulk HNItem upload"""
    data: List[Dict[str, Any]] = Field(..., description="Bulk HN item data")
    source: Optional[str] = Field(None, description="Source description")
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


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
            "transition": transition
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

                created_items.append({
                    "id": response.metadata.id,
                    "hn_id": item_data.get("id"),
                    "status": "created"
                })

            except Exception as e:
                failed_items.append({
                    "hn_id": item_data.get("id"),
                    "error": str(e)
                })

        logger.info("Created %d HNItems, %d failed", len(created_items), len(failed_items))

        return {
            "created": created_items,
            "failed": failed_items,
            "total_created": len(created_items),
            "total_failed": len(failed_items),
            "transition": data.transition
        }, 201

    except Exception as e:
        logger.exception("Error creating HNItem array: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
