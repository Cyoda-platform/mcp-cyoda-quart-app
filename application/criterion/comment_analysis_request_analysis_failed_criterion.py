"""
CommentAnalysisRequestAnalysisFailedCriterion for Cyoda Client Application

Checks if comment analysis failed.
Used in transition from ANALYZING to FAILED state.
"""

import logging
from datetime import datetime, timedelta, timezone
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


class CommentAnalysisRequestAnalysisFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if comment analysis failed.
    Returns True if analysis process encountered errors or couldn't complete.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestAnalysisFailedCriterion",
            description="Check if comment analysis failed",
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

    def _parse_iso_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse ISO timestamp string to datetime object"""
        try:
            # Handle both Z and +00:00 timezone formats
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return None

    async def evaluate(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if comment analysis failed according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            True if analysis process encountered errors or couldn't complete
        """
        try:
            self.logger.debug(
                f"Evaluating analysis failure for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set
            if (
                request.error_message is not None
                and len(request.error_message.strip()) > 0
            ):
                self.logger.debug(
                    f"Request {request.technical_id} has error message: {request.error_message}"
                )
                return True

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

            # Check if any comments failed to analyze after reasonable time (5 minutes)
            current_time = datetime.now(timezone.utc)
            timeout_threshold = timedelta(minutes=5)

            for comment in comments:
                comment_data = comment.data

                # Check if comment is still in FETCHED state
                if comment.get_state() == "fetched":
                    # Check if it's been too long since fetching
                    fetched_at_str = comment_data.get("fetchedAt")
                    if fetched_at_str:
                        fetched_at = self._parse_iso_timestamp(fetched_at_str)
                        if (
                            fetched_at
                            and (current_time - fetched_at) > timeout_threshold
                        ):
                            self.logger.debug(
                                f"Comment {comment.get_id()} stuck in FETCHED state for over 5 minutes - analysis failed"
                            )
                            return True

            self.logger.debug(
                f"CommentAnalysisRequest {request.technical_id}: No analysis failure detected"
            )

            return False

        except Exception as e:
            self.logger.error(
                f"Error evaluating analysis failure criterion for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Return True on error to trigger failure transition
            return True
