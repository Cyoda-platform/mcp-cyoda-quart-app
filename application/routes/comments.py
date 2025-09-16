"""
Comment Routes for Cyoda Client Application

Manages all Comment-related API endpoints including read operations
and filtering as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

from ..entity.comment.version_1.comment import Comment
from ..models import (
    CommentListResponse,
    CommentQueryParams,
    CommentResponse,
    ErrorResponse,
    ValidationErrorResponse,
)


# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


comments_bp = Blueprint("comments", __name__, url_prefix="/api/comments")


@comments_bp.route("", methods=["GET"])
@validate_querystring(CommentQueryParams)
@tag(["comments"])
@operation_id("list_comments")
@validate(
    responses={
        200: (CommentListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_comments(
    query_args: CommentQueryParams,
) -> ResponseReturnValue:
    """Get comments associated with analysis requests"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.analysis_request_id:
            search_conditions["analysisRequestId"] = query_args.analysis_request_id

        if query_args.post_id:
            search_conditions["postId"] = str(query_args.post_id)

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Comment.ENTITY_NAME,
                condition=condition,
                entity_version=str(Comment.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Comment.ENTITY_NAME,
                entity_version=str(Comment.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.page * query_args.size
        end = start + query_args.size
        paginated_entities = entity_list[start:end]

        # Calculate pagination info
        total_elements = len(entity_list)
        total_pages = (total_elements + query_args.size - 1) // query_args.size

        return (
            jsonify(
                {
                    "content": paginated_entities,
                    "totalElements": total_elements,
                    "totalPages": total_pages,
                    "size": query_args.size,
                    "number": query_args.page,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error listing Comments: %s", str(e))
        return jsonify({"error": str(e)}), 500


@comments_bp.route("/<entity_id>", methods=["GET"])
@tag(["comments"])
@operation_id("get_comment")
@validate(
    responses={
        200: (CommentResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_comment(entity_id: str) -> ResponseReturnValue:
    """Get a specific comment by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Comment.ENTITY_NAME,
            entity_version=str(Comment.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Comment not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Comment %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
