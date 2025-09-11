"""
CommentAnalysisRequestHasCommentsCriterion for Cyoda Client Application

Checks if comments were successfully fetched from the API.
Used in transition from FETCHING_COMMENTS to ANALYZING state.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, cast, runtime_checkable

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...
    def get_state(self) -> str: ...

    data: Dict[str, Any]


class _EntityService(Protocol):
    async def search(
        self,
        entity_class: str,
        condition: Any,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...


class CommentAnalysisRequestHasCommentsCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if comments were successfully fetched from the API.
    Returns True if at least one Comment entity exists for this analysis request.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestHasCommentsCriterion",
            description="Check if comments were successfully fetched from the API",
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

    async def evaluate(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if comments were successfully fetched according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            True if at least one Comment entity exists for this analysis request
        """
        try:
            self.logger.debug(
                f"Evaluating comments existence for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Find comments by analysisRequestId
            entity_service = self._get_entity_service()

            # Build search condition to find comments for this request
            from common.service.entity_service import SearchConditionRequest

            condition = (
                SearchConditionRequest.builder()
                .equals("analysisRequestId", str(request.technical_id))
                .build()
            )

            comments = await entity_service.search(
                entity_class="Comment",
                condition=condition,
                entity_version="1",
            )

            has_comments = len(comments) > 0

            self.logger.debug(
                f"CommentAnalysisRequest {request.technical_id} has {len(comments)} comments - criterion result: {has_comments}"
            )

            return has_comments

        except Exception as e:
            self.logger.error(
                f"Error evaluating comments criterion for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Return False on error to prevent transition
            return False
