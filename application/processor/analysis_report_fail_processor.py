"""
AnalysisReportFailProcessor for Cyoda Client Application

Handles email sending failure.
"""

import logging
from typing import Any

from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class AnalysisReportFailProcessor(CyodaProcessor):
    """
    Processor for handling AnalysisReport email sending failures.
    Logs failure details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportFailProcessor",
            description="Handles email sending failure",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle email sending failure according to functional requirements.

        Args:
            entity: The AnalysisReport with email sending failure
            **kwargs: Additional processing parameters

        Returns:
            AnalysisReport with failure logged
        """
        try:
            self.logger.info(
                f"Handling email sending failure for AnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # Log email sending failure
            self.logger.error(
                f"Email sending failed for AnalysisReport {report_entity.technical_id}"
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error handling email failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
