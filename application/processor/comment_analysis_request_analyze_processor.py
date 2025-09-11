"""
CommentAnalysisRequestAnalyzeProcessor for Cyoda Client Application

Triggers analysis of all associated comments by transitioning them to ANALYZED state.
Coordinates the analysis workflow for all comments in the request.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, cast, runtime_checkable

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
    state: str


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

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> _HasMetadata: ...


class CommentAnalysisRequestAnalyzeProcessor(CyodaProcessor):
    """
    Processor for triggering analysis of all associated comments.
    Transitions comments from FETCHED to ANALYZED state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestAnalyzeProcessor",
            description="Trigger analysis of all associated comments",
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
        Trigger analysis of all associated comments according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in FETCHING_COMMENTS state
            **kwargs: Additional processing parameters

        Returns:
            The request entity with all comments analyzed
        """
        try:
            self.logger.info(
                f"Analyzing comments for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
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

            if not comments:
                self.logger.warning(
                    f"No comments found for request {request.technical_id}"
                )
                return request

            # Transition each comment that is in FETCHED state to ANALYZED state
            analyzed_count = 0
            for comment in comments:
                try:
                    if comment.get_state() == "fetched":
                        # Execute transition to ANALYZED state
                        await entity_service.execute_transition(
                            entity_id=comment.get_id(),
                            transition="transition_to_analyzed",
                            entity_class="Comment",
                            entity_version="1",
                        )
                        analyzed_count += 1
                        self.logger.debug(
                            f"Transitioned Comment {comment.get_id()} to ANALYZED state"
                        )

                except Exception as e:
                    self.logger.error(
                        f"Failed to analyze Comment {comment.get_id()}: {str(e)}"
                    )
                    # Continue with other comments even if one fails
                    continue

            self.logger.info(
                f"Successfully analyzed {analyzed_count} comments for request {request.technical_id}"
            )

            return request

        except Exception as e:
            self.logger.error(
                f"Error analyzing comments for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
