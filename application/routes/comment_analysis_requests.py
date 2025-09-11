"""
CommentAnalysisRequest Routes for Cyoda Client Application

Manages all CommentAnalysisRequest-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import validate_querystring, validate_request

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)

comment_analysis_requests_bp = Blueprint(
    "comment_analysis_requests", __name__, url_prefix="/api/comment-analysis-requests"
)


# ---- Service typing ---------------------------------------------------------


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...

    def get_state(self) -> str: ...

    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...

    async def find_all(
        self, *, entity_class: str, entity_version: str
    ) -> List[_ListedEntity]: ...

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...

    async def delete_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> None: ...

    async def execute_transition(
        self,
        *,
        entity_id: str,
        transition: str,
        entity_class: str,
        entity_version: str,
    ) -> _SavedEntity: ...


# Services will be accessed through the registry
entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Request/Query Models ---------------------------------------------------


class CommentAnalysisRequestQueryParams(BaseModel):
    """Query parameters for CommentAnalysisRequest listing"""

    requested_by: Optional[str] = Field(
        default=None, alias="requestedBy", description="Filter by email"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    page: int = Field(default=0, description="Page number")
    size: int = Field(default=20, description="Page size")


class CommentAnalysisRequestCreateRequest(BaseModel):
    """Request model for creating a CommentAnalysisRequest"""

    post_id: int = Field(
        ..., alias="postId", description="The post ID to fetch comments for"
    )
    requested_by: str = Field(
        ..., alias="requestedBy", description="Email address of the requester"
    )


# ---- Routes -----------------------------------------------------------------


@comment_analysis_requests_bp.route("", methods=["POST"])
@validate_request(CommentAnalysisRequestCreateRequest)
async def create_comment_analysis_request(
    data: CommentAnalysisRequestCreateRequest,
) -> ResponseReturnValue:
    """Create a new CommentAnalysisRequest"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Save the entity (starts in INITIAL state automatically)
        response = await service.save(
            entity=entity_data,
            entity_class="CommentAnalysisRequest",
            entity_version="1",
        )

        logger.info("Created CommentAnalysisRequest with ID: %s", response.metadata.id)

        # Convert to API response format
        result_data = dict(response.data)
        result_data["id"] = response.metadata.id
        result_data["state"] = response.metadata.state

        return jsonify(result_data), 201

    except Exception as e:
        logger.exception("Error creating CommentAnalysisRequest: %s", str(e))
        return jsonify({"error": str(e)}), 500


@comment_analysis_requests_bp.route("/<entity_id>", methods=["GET"])
async def get_comment_analysis_request(entity_id: str) -> ResponseReturnValue:
    """Get CommentAnalysisRequest by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class="CommentAnalysisRequest",
            entity_version="1",
        )

        if not response:
            return jsonify({"error": "Comment analysis request not found"}), 404

        # Convert to API response format
        entity_data: Dict[str, Any] = dict(response.data)
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:
        logger.exception(
            "Error getting CommentAnalysisRequest %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@comment_analysis_requests_bp.route("", methods=["GET"])
@validate_querystring(CommentAnalysisRequestQueryParams)
async def list_comment_analysis_requests(
    query_args: CommentAnalysisRequestQueryParams,
) -> ResponseReturnValue:
    """List CommentAnalysisRequests with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.requested_by:
            search_conditions["requestedBy"] = query_args.requested_by

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class="CommentAnalysisRequest",
                condition=condition,
                entity_version="1",
            )
        else:
            entities = await service.find_all(
                entity_class="CommentAnalysisRequest", entity_version="1"
            )

        # Convert to API response format
        entity_list: List[Dict[str, Any]] = []
        for entity in entities:
            entity_data = {
                "id": entity.get_id(),
                "postId": entity.data.get("postId"),
                "requestedBy": entity.data.get("requestedBy"),
                "state": entity.get_state(),
                "createdAt": entity.data.get("createdAt"),
                "completedAt": entity.data.get("completedAt"),
                "errorMessage": entity.data.get("errorMessage"),
            }
            entity_list.append(entity_data)

        # Apply pagination
        start = query_args.page * query_args.size
        end = start + query_args.size
        paginated_entities = entity_list[start:end]

        return (
            jsonify(
                {
                    "content": paginated_entities,
                    "totalElements": len(entity_list),
                    "totalPages": (len(entity_list) + query_args.size - 1)
                    // query_args.size,
                    "size": query_args.size,
                    "number": query_args.page,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing CommentAnalysisRequests: %s", str(e))
        return jsonify({"error": str(e)}), 500


@comment_analysis_requests_bp.route("/<entity_id>/retry", methods=["PUT"])
async def retry_comment_analysis_request(entity_id: str) -> ResponseReturnValue:
    """Retry a failed comment analysis request"""
    try:
        service = get_services()

        # Execute manual transition from FAILED to PENDING
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="transition_to_pending",
            entity_class="CommentAnalysisRequest",
            entity_version="1",
        )

        logger.info("Retried CommentAnalysisRequest %s", entity_id)

        # Convert to API response format
        entity_data: Dict[str, Any] = dict(response.data)
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:
        logger.exception(
            "Error retrying CommentAnalysisRequest %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@comment_analysis_requests_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_comment_analysis_request(entity_id: str) -> ResponseReturnValue:
    """Delete CommentAnalysisRequest"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class="CommentAnalysisRequest",
            entity_version="1",
        )

        logger.info("Deleted CommentAnalysisRequest %s", entity_id)

        return "", 204

    except Exception as e:
        logger.exception(
            "Error deleting CommentAnalysisRequest %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
