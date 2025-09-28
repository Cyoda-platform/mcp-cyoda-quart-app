"""
Comment Ingestion Routes for Cyoda Client Application

Handles ingestion of comments from JSONPlaceholder API and creation of analysis reports.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx
from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate

from application.entity.comment.version_1.comment import Comment
from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from application.models import (
    CommentIngestionRequest,
    CommentIngestionResponse,
    ErrorResponse,
    JSONPlaceholderComment,
    ValidationErrorResponse,
)
from services.services import get_entity_service

logger = logging.getLogger(__name__)

ingestion_bp = Blueprint("ingestion", __name__, url_prefix="/api/ingestion")


@ingestion_bp.route("/comments", methods=["POST"])
@tag(["ingestion"])
@operation_id("ingest_comments")
@validate(
    request=CommentIngestionRequest,
    responses={
        200: (CommentIngestionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def ingest_comments(data: CommentIngestionRequest) -> ResponseReturnValue:
    """
    Ingest comments from JSONPlaceholder API for a specific post and create analysis report.

    This endpoint:
    1. Fetches comments from JSONPlaceholder API for the specified post
    2. Creates Comment entities in the system
    3. Creates a CommentAnalysisReport entity for the post
    4. Triggers the workflow to analyze comments and send email report
    """
    try:
        logger.info(f"Starting comment ingestion for post {data.post_id}")

        # Fetch comments from JSONPlaceholder API
        comments_data = await _fetch_comments_from_api(data.post_id)

        if not comments_data:
            return {
                "error": f"No comments found for post {data.post_id}",
                "code": "NO_COMMENTS_FOUND",
            }, 400

        # Create Comment entities
        created_comments = await _create_comment_entities(comments_data)

        # Create CommentAnalysisReport entity
        report_id = await _create_analysis_report(data.post_id, data.recipient_email)

        logger.info(
            f"Successfully ingested {len(created_comments)} comments for post {data.post_id}, "
            f"created report {report_id}"
        )

        response = CommentIngestionResponse(
            success=True,
            message=f"Successfully ingested {len(created_comments)} comments and created analysis report",
            post_id=data.post_id,
            comments_ingested=len(created_comments),
            report_id=report_id,
        )

        return response.model_dump(), 200

    except Exception as e:
        logger.exception(f"Error ingesting comments for post {data.post_id}: {str(e)}")
        return {"error": str(e), "code": "INGESTION_ERROR"}, 500


async def _fetch_comments_from_api(post_id: int) -> List[Dict[str, Any]]:
    """
    Fetch comments from JSONPlaceholder API for a specific post.

    Args:
        post_id: The post ID to fetch comments for

    Returns:
        List of comment dictionaries from the API
    """
    try:
        url = f"https://jsonplaceholder.typicode.com/comments?postId={post_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            comments_data = response.json()
            logger.info(
                f"Fetched {len(comments_data)} comments from API for post {post_id}"
            )

            return comments_data

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching comments for post {post_id}: {str(e)}")
        raise Exception(f"Failed to fetch comments from API: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
        raise


async def _create_comment_entities(comments_data: List[Dict[str, Any]]) -> List[str]:
    """
    Create Comment entities from JSONPlaceholder API data.

    Args:
        comments_data: List of comment dictionaries from the API

    Returns:
        List of created comment entity IDs
    """
    entity_service = get_entity_service()
    created_comment_ids = []

    for comment_data in comments_data:
        try:
            # Validate the comment data structure
            api_comment = JSONPlaceholderComment(**comment_data)

            # Create Comment entity
            comment = Comment(
                post_id=api_comment.postId,
                comment_id=api_comment.id,
                name=api_comment.name,
                email=api_comment.email,
                body=api_comment.body,
            )

            # Save the comment entity
            response = await entity_service.save(
                entity=comment.model_dump(by_alias=True),
                entity_class=Comment.ENTITY_NAME,
                entity_version=str(Comment.ENTITY_VERSION),
            )

            created_comment_ids.append(response.metadata.id)
            logger.debug(
                f"Created Comment entity {response.metadata.id} for comment {api_comment.id}"
            )

        except Exception as e:
            logger.warning(
                f"Failed to create Comment entity for comment {comment_data.get('id', 'unknown')}: {str(e)}"
            )
            # Continue with other comments even if one fails
            continue

    return created_comment_ids


async def _create_analysis_report(post_id: int, recipient_email: str) -> str:
    """
    Create a CommentAnalysisReport entity for the post.

    Args:
        post_id: The post ID to create report for
        recipient_email: Email address to send the report to

    Returns:
        The created report entity ID
    """
    entity_service = get_entity_service()

    try:
        # Create CommentAnalysisReport entity
        report = CommentAnalysisReport(
            post_id=post_id,
            report_title=f"Comment Analysis Report for Post {post_id}",
            recipient_email=recipient_email,
        )

        # Save the report entity
        response = await entity_service.save(
            entity=report.model_dump(by_alias=True),
            entity_class=CommentAnalysisReport.ENTITY_NAME,
            entity_version=str(CommentAnalysisReport.ENTITY_VERSION),
        )

        logger.info(
            f"Created CommentAnalysisReport entity {response.metadata.id} for post {post_id}"
        )
        return response.metadata.id

    except Exception as e:
        logger.error(
            f"Failed to create CommentAnalysisReport for post {post_id}: {str(e)}"
        )
        raise
