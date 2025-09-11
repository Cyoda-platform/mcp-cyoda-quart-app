"""
CommentAnalysisReportSendProcessor for Cyoda Client Application

Sends report via email to the requester.
Simulates email sending and marks report as sent.
"""

import logging

from typing import Any, Dict, List, Optional, Protocol, cast, runtime_checkable

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
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


class CommentAnalysisReportSendProcessor(CyodaProcessor):
    """
    Processor for sending report via email to the requester.
    Simulates email service and marks report as sent.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisReportSendProcessor",
            description="Send report via email to the requester",
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

    async def _simulate_email_service(
        self, recipient_email: str, subject: str, body: str
    ) -> bool:
        """
        Simulate email sending service.
        In a real implementation, this would integrate with an actual email service.

        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body content

        Returns:
            True if email was "sent" successfully, False otherwise
        """
        try:
            # Simulate email sending logic
            # In real implementation, this would call an email service like SendGrid, SES, etc.

            # Basic validation
            if not recipient_email or "@" not in recipient_email:
                self.logger.error(f"Invalid recipient email: {recipient_email}")
                return False

            if not subject or not body:
                self.logger.error("Email subject or body is empty")
                return False

            # Simulate some processing time and potential failure
            # For demo purposes, we'll assume 95% success rate
            import random

            success = random.random() > 0.05  # 95% success rate

            if success:
                self.logger.info(f"Email successfully sent to {recipient_email}")
                self.logger.debug(f"Email subject: {subject}")
                self.logger.debug(f"Email body length: {len(body)} characters")
            else:
                self.logger.warning(
                    f"Simulated email sending failure to {recipient_email}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Email service error: {str(e)}")
            return False

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send report via email according to functional requirements.

        Args:
            entity: The CommentAnalysisReport in GENERATED state
            **kwargs: Additional processing parameters

        Returns:
            The report entity with email sent status updated
        """
        try:
            self.logger.info(
                f"Sending email for CommentAnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Find the CommentAnalysisRequest to get the requester email
            entity_service = self._get_entity_service()

            # Build search condition to find the analysis request
            from common.service.entity_service import SearchConditionRequest

            # Search by technical_id (the analysis_request_id should be the technical_id)
            condition = (
                SearchConditionRequest.builder()
                .equals("technical_id", str(report.analysis_request_id))
                .build()
            )

            requests = await entity_service.search(
                entity_class="CommentAnalysisRequest",
                condition=condition,
                entity_version="1",
            )

            if not requests:
                self.logger.error(
                    f"No CommentAnalysisRequest found with ID {report.analysis_request_id}"
                )
                return report

            # Get the analysis request data
            request_data = requests[0].data
            recipient_email = request_data.get("requestedBy", "")
            post_id = request_data.get("postId", "unknown")

            if not recipient_email:
                self.logger.error("No recipient email found in analysis request")
                return report

            # Prepare email content
            email_subject = f"Comment Analysis Report for Post {post_id}"
            email_body = report.report_content

            # Send email using simulated email service
            success = await self._simulate_email_service(
                recipient_email, email_subject, email_body
            )

            if success:
                # Mark report as sent
                report.set_sent()
                self.logger.info(
                    f"Report {report.technical_id} sent successfully to {recipient_email}"
                )
            else:
                self.logger.error(
                    f"Failed to send report {report.technical_id} to {recipient_email}"
                )

            return report

        except Exception as e:
            self.logger.error(
                f"Error sending email for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
