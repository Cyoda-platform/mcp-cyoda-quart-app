"""
AnalysisReportRetryProcessor for Cyoda Client Application

Resets the report for retry email sending.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.analysis_report.version_1.analysis_report import AnalysisReport


class AnalysisReportRetryProcessor(CyodaProcessor):
    """
    Processor for retrying AnalysisReport email sending.
    Clears emailSentAt timestamp for retry.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportRetryProcessor",
            description="Resets the report for retry email sending",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reset the report for retry email sending according to functional requirements.

        Args:
            entity: The AnalysisReport in FAILED state
            **kwargs: Additional processing parameters

        Returns:
            AnalysisReport ready for retry
        """
        try:
            self.logger.info(
                f"Preparing email retry for AnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # Clear emailSentAt for retry
            report_entity.clear_email_sent()

            self.logger.info(
                f"AnalysisReport {report_entity.technical_id} prepared for email retry"
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error preparing email retry for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
