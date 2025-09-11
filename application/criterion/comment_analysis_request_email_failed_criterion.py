"""
CommentAnalysisRequestEmailFailedCriterion for Cyoda Client Application

Checks if email sending failed.
Used in transition from SENDING_REPORT to FAILED state.
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


class CommentAnalysisRequestEmailFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if email sending failed.
    Returns True if report exists but failed to send via email.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestEmailFailedCriterion",
            description="Check if email sending failed",
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
        Check if email sending failed according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            True if report exists but failed to send via email
        """
        try:
            self.logger.debug(
                f"Evaluating email failure for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set on the request
            if (
                request.error_message is not None
                and len(request.error_message.strip()) > 0
            ):
                self.logger.debug(
                    f"Request {request.technical_id} has error message: {request.error_message}"
                )
                return True

            # Find report by analysisRequestId
            entity_service = self._get_entity_service()

            # Build search condition to find report for this request
            from common.service.entity_service import SearchConditionRequest

            condition = (
                SearchConditionRequest.builder()
                .equals("analysisRequestId", str(request.technical_id))
                .build()
            )

            reports = await entity_service.search(
                entity_class="CommentAnalysisReport",
                condition=condition,
                entity_version="1",
            )

            # If no report found, email sending failed
            if len(reports) == 0:
                self.logger.debug(
                    f"No report found for request {request.technical_id} - email failed"
                )
                return True

            # Check if report is in FAILED_TO_SEND state
            report = reports[0]
            report_state = report.get_state()

            email_failed = report_state == "failed_to_send"

            self.logger.debug(
                f"CommentAnalysisRequest {request.technical_id}: Report state is {report_state} - email failed criterion result: {email_failed}"
            )

            return email_failed

        except Exception as e:
            self.logger.error(
                f"Error evaluating email failure criterion for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Return True on error to trigger failure transition
            return True
