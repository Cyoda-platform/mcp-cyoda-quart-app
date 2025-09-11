"""
CommentAnalysisReportRetryProcessor for Cyoda Client Application

Resets report for retry sending.
Clears sent timestamp to allow email resending.
"""

import logging
from typing import Any

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisReportRetryProcessor(CyodaProcessor):
    """
    Processor for resetting report for retry sending.
    Clears sent timestamp to allow email resending.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisReportRetryProcessor",
            description="Reset report for retry sending",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reset report for retry sending according to functional requirements.

        Args:
            entity: The CommentAnalysisReport in FAILED_TO_SEND state
            **kwargs: Additional processing parameters

        Returns:
            The report entity ready for retry
        """
        try:
            self.logger.info(
                f"Resetting CommentAnalysisReport {getattr(entity, 'technical_id', '<unknown>')} for retry"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Clear sent timestamp for retry
            report.clear_sent()  # This sets sentAt = None

            self.logger.info(
                f"CommentAnalysisReport {report.technical_id} reset for retry - sent timestamp cleared"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error resetting report {getattr(entity, 'technical_id', '<unknown>')} for retry: {str(e)}"
            )
            raise
