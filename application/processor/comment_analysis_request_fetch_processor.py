"""
CommentAnalysisRequestFetchProcessor for Cyoda Client Application

Fetches comments from JSONPlaceholder API for the given postId.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.comment_analysis_request.version_1.comment_analysis_request import CommentAnalysisRequest
from application.entity.comment.version_1.comment import Comment
from services.services import get_entity_service


class CommentAnalysisRequestFetchProcessor(CyodaProcessor):
    """
    Processor for fetching comments from JSONPlaceholder API.
    Creates Comment entities for each fetched comment.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFetchProcessor",
            description="Fetches comments from JSONPlaceholder API for the given postId",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Fetch comments from JSONPlaceholder API according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in PENDING state
            **kwargs: Additional processing parameters

        Returns:
            The entity with associated Comment entities created
        """
        try:
            self.logger.info(
                f"Fetching comments for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Build API URL
            api_url = f"https://jsonplaceholder.typicode.com/comments?postId={request_entity.post_id}"
            
            try:
                # Fetch comments from API
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_url, timeout=30.0)
                    
                if response.status_code == 200:
                    comments_data = response.json()
                    
                    if not isinstance(comments_data, list):
                        raise ValueError("API response is not a list")
                    
                    # Create Comment entities for each comment
                    await self._create_comment_entities(comments_data, request_entity)
                    
                    self.logger.info(
                        f"Successfully fetched {len(comments_data)} comments for post {request_entity.post_id}"
                    )
                else:
                    error_msg = f"Failed to fetch comments: HTTP {response.status_code}"
                    request_entity.set_error(error_msg)
                    raise Exception(error_msg)
                    
            except httpx.TimeoutException:
                error_msg = "Timeout while fetching comments from API"
                request_entity.set_error(error_msg)
                raise Exception(error_msg)
            except httpx.RequestError as e:
                error_msg = f"Request error while fetching comments: {str(e)}"
                request_entity.set_error(error_msg)
                raise Exception(error_msg)
            except json.JSONDecodeError:
                error_msg = "Invalid JSON response from API"
                request_entity.set_error(error_msg)
                raise Exception(error_msg)

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error fetching comments for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Set error message if not already set
            if hasattr(entity, 'error_message') and not entity.error_message:
                entity.error_message = str(e)
            raise

    async def _create_comment_entities(
        self, comments_data: List[Dict[str, Any]], request_entity: CommentAnalysisRequest
    ) -> None:
        """
        Create Comment entities from API response data.

        Args:
            comments_data: List of comment data from API
            request_entity: The CommentAnalysisRequest entity
        """
        entity_service = get_entity_service()
        current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        for comment_data in comments_data:
            try:
                # Create Comment using Pydantic model construction
                comment = Comment(
                    comment_id=comment_data.get("id"),
                    post_id=comment_data.get("postId"),
                    name=comment_data.get("name", ""),
                    email=comment_data.get("email", ""),
                    body=comment_data.get("body", ""),
                    analysis_request_id=request_entity.technical_id or request_entity.entity_id,
                    fetched_at=current_timestamp,
                )

                # Convert Pydantic model to dict for EntityService.save()
                comment_data_dict = comment.model_dump(by_alias=True)

                # Save the new Comment using entity constants
                response = await entity_service.save(
                    entity=comment_data_dict,
                    entity_class=Comment.ENTITY_NAME,
                    entity_version=str(Comment.ENTITY_VERSION),
                )

                # Get the technical ID of the created entity
                created_entity_id = response.metadata.id

                self.logger.debug(
                    f"Created Comment {created_entity_id} for post {comment.post_id}"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to create Comment for comment ID {comment_data.get('id', 'unknown')}: {str(e)}"
                )
                # Continue with other comments even if one fails
                continue
