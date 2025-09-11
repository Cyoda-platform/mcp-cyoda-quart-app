"""
CommentAnalysisRequestAnalysisCompleteCriterion for Cyoda Client Application

Checks if all associated comments have been analyzed.
Used in transition from ANALYZING to SENDING_REPORT state.
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


class CommentAnalysisRequestAnalysisCompleteCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if all associated comments have been analyzed.
    Returns True if all Comment entities for this request are in ANALYZED state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestAnalysisCompleteCriterion",
            description="Check if all associated comments have been analyzed",
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
        Check if all comments have been analyzed according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            True if all Comment entities for this request are in ANALYZED state
        """
        try:
            self.logger.debug(
                f"Evaluating analysis completion for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
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

            # If no comments found, analysis cannot be complete
            if len(comments) == 0:
                self.logger.debug(
                    f"No comments found for request {request.technical_id} - analysis not complete"
                )
                return False

            # Check if all comments are in ANALYZED state
            analyzed_count = 0
            for comment in comments:
                if comment.get_state() == "analyzed":
                    analyzed_count += 1

            all_analyzed = analyzed_count == len(comments)

            self.logger.debug(
                f"CommentAnalysisRequest {request.technical_id}: {analyzed_count}/{len(comments)} comments analyzed - criterion result: {all_analyzed}"
            )

            return all_analyzed

        except Exception as e:
            self.logger.error(
                f"Error evaluating analysis completion criterion for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Return False on error to prevent transition
            return False
