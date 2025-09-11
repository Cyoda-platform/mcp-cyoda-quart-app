"""
CommentAnalysisRequestEmailProcessor for Cyoda Client Application

Sends the analysis report via email and marks the request as completed.
Handles email delivery coordination and completion tracking.
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


class CommentAnalysisRequestEmailProcessor(CyodaProcessor):
    """
    Processor for sending the analysis report via email.
    Checks if report was sent and marks request as completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestEmailProcessor",
            description="Send the analysis report via email",
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
        Send the analysis report via email according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in SENDING_REPORT state
            **kwargs: Additional processing parameters

        Returns:
            The request entity with completedAt timestamp set if successful
        """
        try:
            self.logger.info(
                f"Checking email status for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

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

            if not reports:
                error_msg = "No report found for this analysis request"
                request.set_error(error_msg)
                self.logger.error(f"No report found for request {request.technical_id}")
                return request

            # Get the first (and should be only) report
            report = reports[0]

            # Check if report was sent successfully
            if report.get_state() == "sent":
                # Mark request as completed
                request.set_completed()
                self.logger.info(
                    f"Email sent successfully for request {request.technical_id}, marking as completed"
                )
            else:
                # Report failed to send
                error_msg = "Failed to send email report"
                request.set_error(error_msg)
                self.logger.error(
                    f"Email failed to send for request {request.technical_id}"
                )

            return request

        except Exception as e:
            # Set error message on the request
            request = cast_entity(entity, CommentAnalysisRequest)
            error_msg = f"Email processing failed: {str(e)}"
            request.set_error(error_msg)

            self.logger.error(
                f"Error processing email for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return request
