"""
CommentAnalysisRequestFetchSuccessCriterion for Cyoda Client Application

Checks if comments were successfully fetched from the API.
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


class CommentAnalysisRequestFetchSuccessCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if comments were successfully fetched from the API.
    Condition: Comments exist for the analysis request and no error message is set.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFetchSuccessCriterion",
            description="Checks if comments were successfully fetched from the API",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if comments were successfully fetched according to functional requirements.

        Args:
            entity: The CyodaEntity to check (expected to be CommentAnalysisRequest)
            **kwargs: Additional criteria parameters

        Returns:
            True if comments exist and no error message is set, False otherwise
        """
        try:
            self.logger.info(
                f"Checking fetch success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set
            if request_entity.error_message is not None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has error message: {request_entity.error_message}"
                )
                return False

            # Find comments by analysis request ID
            comments = await self._find_comments_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            # Check if comments exist
            comments_exist = len(comments) > 0

            if comments_exist:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has {len(comments)} comments - fetch successful"
                )
            else:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no comments - fetch failed"
                )

            return comments_exist

        except Exception as e:
            self.logger.error(
                f"Error checking fetch success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

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
