"""
CommentAnalysisRequestFetchProcessor for Cyoda Client Application

Fetches comments from JSONPlaceholder API and creates Comment entities.
Handles API communication and error scenarios.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, cast, runtime_checkable

import aiohttp  # type: ignore

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class CommentAnalysisRequestFetchProcessor(CyodaProcessor):
    """
    Processor for fetching comments from JSONPlaceholder API.
    Creates Comment entities for each fetched comment.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFetchProcessor",
            description="Fetch comments from JSONPlaceholder API and create Comment entities",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Fetch comments from JSONPlaceholder API according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in PENDING state
            **kwargs: Additional processing parameters

        Returns:
            The request entity with associated Comment entities created
        """
        try:
            self.logger.info(
                f"Fetching comments for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Fetch comments from JSONPlaceholder API
            api_url = f"https://jsonplaceholder.typicode.com/comments?postId={request.post_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        error_msg = f"API request failed with status {response.status}"
                        request.set_error(error_msg)
                        self.logger.error(f"Failed to fetch comments: {error_msg}")
                        return request

                    comments_data = await response.json()

            if not comments_data:
                error_msg = "No comments found for the specified post ID"
                request.set_error(error_msg)
                self.logger.warning(f"No comments found for post {request.post_id}")
                return request

            # Create Comment entities for each fetched comment
            entity_service = self._get_entity_service()
            created_comments = 0

            for comment_data in comments_data:
                try:
                    # Count words in comment body
                    word_count = (
                        len(comment_data.get("body", "").strip().split())
                        if comment_data.get("body")
                        else 0
                    )

                    # Create Comment entity data
                    comment_entity_data: Dict[str, Any] = {
                        "id": comment_data.get("id"),
                        "postId": comment_data.get("postId"),
                        "name": comment_data.get("name", ""),
                        "email": comment_data.get("email", ""),
                        "body": comment_data.get("body", ""),
                        "analysisRequestId": request.technical_id,
                        "wordCount": word_count,
                        "fetchedAt": datetime.now(timezone.utc)
                        .isoformat()
                        .replace("+00:00", "Z"),
                    }

                    # Save the new Comment entity with transition to FETCHED state
                    response = await entity_service.save(
                        entity=comment_entity_data,
                        entity_class="Comment",
                        entity_version="1",
                    )

                    # Execute transition to FETCHED state
                    await entity_service.execute_transition(
                        entity_id=response.metadata.id,
                        transition="transition_to_fetched",
                        entity_class="Comment",
                        entity_version="1",
                    )

                    created_comments += 1
                    self.logger.debug(
                        f"Created Comment {response.metadata.id} for request {request.technical_id}"
                    )

                except Exception as e:
                    self.logger.error(f"Failed to create Comment entity: {str(e)}")
                    # Continue with other comments even if one fails
                    continue

            self.logger.info(
                f"Successfully created {created_comments} Comment entities for request {request.technical_id}"
            )

            return request

        except Exception as e:
            # Set error message on the request
            error_msg = f"Failed to fetch comments: {str(e)}"
            request = cast_entity(entity, CommentAnalysisRequest)
            request.set_error(error_msg)

            self.logger.error(
                f"Error fetching comments for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return request
