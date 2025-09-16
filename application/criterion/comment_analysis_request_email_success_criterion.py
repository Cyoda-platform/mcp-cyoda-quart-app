"""
CommentAnalysisRequestEmailSuccessCriterion for Cyoda Client Application

Checks if the email report was sent successfully.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from common.service.entity_service import SearchConditionRequest
from application.entity.comment_analysis_request.version_1.comment_analysis_request import CommentAnalysisRequest
from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from services.services import get_entity_service


class CommentAnalysisRequestEmailSuccessCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if the email report was sent successfully.
    Condition: Associated analysis report has emailSentAt timestamp set.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestEmailSuccessCriterion",
            description="Checks if the email report was sent successfully",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the email report was sent successfully according to functional requirements.

        Args:
            entity: The CyodaEntity to check (expected to be CommentAnalysisRequest)
            **kwargs: Additional criteria parameters

        Returns:
            True if associated analysis report has emailSentAt timestamp set, False otherwise
        """
        try:
            self.logger.info(
                f"Checking email success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set
            if request_entity.error_message is not None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has error message: {request_entity.error_message}"
                )
                return False

            # Find analysis report by request ID
            report = await self._find_analysis_report_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            if report is None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no analysis report"
                )
                return False

            # Check if email was sent
            email_sent = report.email_sent_at is not None

            if email_sent:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has email sent at: {report.email_sent_at}"
                )
            else:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no email sent timestamp"
                )

            return email_sent

        except Exception as e:
            self.logger.error(
                f"Error checking email success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _find_analysis_report_by_request_id(self, request_id: str) -> AnalysisReport | None:
        """
        Find analysis report by request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            AnalysisReport entity or None if not found
        """
        try:
            entity_service = get_entity_service()

            # Build search condition
            builder = SearchConditionRequest.builder()
            builder.equals("analysisRequestId", request_id)
            condition = builder.build()

            # Search for analysis report
            results = await entity_service.search(
                entity_class=AnalysisReport.ENTITY_NAME,
                condition=condition,
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )

            if not results:
                return None

            # Convert first result to AnalysisReport entity
            report_data = results[0].data
            if hasattr(report_data, 'model_dump'):
                report_dict = report_data.model_dump()
            else:
                report_dict = report_data

            return AnalysisReport(**report_dict)

        except Exception as e:
            self.logger.warning(f"Failed to find analysis report for request {request_id}: {str(e)}")
            return None
