"""
CommentAnalysisReportFailProcessor for Cyoda Client Application

Handles email sending failures for reports.
Provides logging and error tracking for failed email deliveries.
"""

import logging
from typing import Any

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisReportFailProcessor(CyodaProcessor):
    """
    Processor for handling email sending failures.
    Logs failures for monitoring and tracking.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisReportFailProcessor",
            description="Handle email sending failures",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle email sending failures according to functional requirements.

        Args:
            entity: The CommentAnalysisReport that failed to send
            **kwargs: Additional processing parameters

        Returns:
            The report entity with failure handled
        """
        try:
            self.logger.info(
                f"Handling email failure for CommentAnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Log the failure for monitoring
            self.logger.error(f"Failed to send report {report.technical_id}")

            # Additional logging for debugging
            self.logger.error(
                f"Report details - Analysis Request ID: {report.analysis_request_id}"
            )
            self.logger.error(f"Report generated at: {report.generated_at}")
            self.logger.error(f"Total comments in report: {report.total_comments}")

            # Update timestamp to track when failure was processed
            report.update_timestamp()

            return report

        except Exception as e:
            self.logger.error(
                f"Error handling failure for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
