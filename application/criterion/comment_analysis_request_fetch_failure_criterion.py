"""
CommentAnalysisRequestFetchFailureCriterion for Cyoda Client Application

Checks if comment fetching failed.
"""

from typing import Any, List

from application.entity.comment.version_1.comment import Comment
from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class CommentAnalysisRequestFetchFailureCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if comment fetching failed.
    Condition: Error message is set or no comments were fetched.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFetchFailureCriterion",
            description="Checks if comment fetching failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if comment fetching failed according to functional requirements.

        Args:
            entity: The CyodaEntity to check (expected to be CommentAnalysisRequest)
            **kwargs: Additional criteria parameters

        Returns:
            True if error message is set or no comments were fetched, False otherwise
        """
        try:
            self.logger.info(
                f"Checking fetch failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set
            if request_entity.error_message is not None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has error message: {request_entity.error_message}"
                )
                return True

            # Find comments by analysis request ID
            comments = await self._find_comments_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            # Check if no comments were fetched
            no_comments = len(comments) == 0

            if no_comments:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no comments - fetch failed"
                )
            else:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has {len(comments)} comments - fetch successful"
                )

            return no_comments

        except Exception as e:
            self.logger.error(
                f"Error checking fetch failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return True  # Assume failure on error

    async def _find_comments_by_request_id(self, request_id: str) -> List[Any]:
        """
        Find comments by analysis request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            List of comments
        """
        try:
            entity_service = get_entity_service()

            # Build search condition
            builder = SearchConditionRequest.builder()
            builder.equals("analysisRequestId", request_id)
            condition = builder.build()

            # Search for comments
            results = await entity_service.search(
                entity_class=Comment.ENTITY_NAME,
                condition=condition,
                entity_version=str(Comment.ENTITY_VERSION),
            )

            return results

        except Exception as e:
            self.logger.warning(
                f"Failed to find comments for request {request_id}: {str(e)}"
            )
            return []
