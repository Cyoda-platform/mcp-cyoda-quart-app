"""
AnalysisReportSentProcessor for Cyoda Client Application

Marks the report as successfully sent.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.analysis_report.version_1.analysis_report import AnalysisReport


class AnalysisReportSentProcessor(CyodaProcessor):
    """
    Processor for marking AnalysisReport as successfully sent.
    Sets the emailSentAt timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportSentProcessor",
            description="Marks the report as successfully sent",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Mark the report as successfully sent according to functional requirements.

        Args:
            entity: The AnalysisReport with successful email sending
            **kwargs: Additional processing parameters

        Returns:
            Updated AnalysisReport with emailSentAt timestamp
        """
        try:
            self.logger.info(
                f"Marking AnalysisReport as sent {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # Set emailSentAt to current timestamp
            report_entity.set_email_sent()

            self.logger.info(
                f"AnalysisReport {report_entity.technical_id} marked as sent"
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error marking report as sent for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
