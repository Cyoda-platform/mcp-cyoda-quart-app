"""
Comment Routes for Cyoda Client Application

Manages all Comment-related API endpoints for retrieving comments
associated with analysis requests as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)

comments_bp = Blueprint("comments", __name__)


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
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...


# Services will be accessed through the registry
entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Routes -----------------------------------------------------------------


@comments_bp.route(
    "/api/comment-analysis-requests/<request_id>/comments", methods=["GET"]
)
async def get_comments_by_analysis_request(request_id: str) -> ResponseReturnValue:
    """Retrieve all comments associated with a specific analysis request"""
    try:
        service = get_services()

        # Build search condition to find comments for this request
        condition = (
            SearchConditionRequest.builder()
            .equals("analysisRequestId", request_id)
            .build()
        )

        comments = await service.search(
            entity_class="Comment",
            condition=condition,
            entity_version="1",
        )

        # Convert to API response format
        comment_list: List[Dict[str, Any]] = []
        for comment in comments:
            comment_data = {
                "id": comment.data.get("id"),
                "postId": comment.data.get("postId"),
                "name": comment.data.get("name"),
                "email": comment.data.get("email"),
                "body": comment.data.get("body"),
                "analysisRequestId": comment.data.get("analysisRequestId"),
                "sentiment": comment.data.get("sentiment"),
                "wordCount": comment.data.get("wordCount"),
                "state": comment.get_state(),
                "fetchedAt": comment.data.get("fetchedAt"),
            }
            comment_list.append(comment_data)

        return jsonify(comment_list), 200

    except Exception as e:
        logger.exception(
            "Error getting comments for request %s: %s", request_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@comments_bp.route("/api/comments/<entity_id>", methods=["GET"])
async def get_comment(entity_id: str) -> ResponseReturnValue:
    """Retrieve a specific comment by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="Comment", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Comment not found"}), 404

        # Convert to API response format
        comment_data = {
            "id": response.data.get("id"),
            "postId": response.data.get("postId"),
            "name": response.data.get("name"),
            "email": response.data.get("email"),
            "body": response.data.get("body"),
            "analysisRequestId": response.data.get("analysisRequestId"),
            "sentiment": response.data.get("sentiment"),
            "wordCount": response.data.get("wordCount"),
            "state": response.metadata.state,
            "fetchedAt": response.data.get("fetchedAt"),
        }

        return jsonify(comment_data), 200

    except Exception as e:
        logger.exception("Error getting Comment %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500
