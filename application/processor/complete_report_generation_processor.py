"""
CompleteReportGenerationProcessor for Cyoda Client Application

Handles the finalization of report generation.
Compiles final summary and prepares report for sending as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.report.version_1.report import Report


class CompleteReportGenerationProcessor(CyodaProcessor):
    """
    Processor for Report that finalizes report generation.
    Compiles final summary and marks report as ready for sending.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteReportGenerationProcessor",
            description="Finalizes report generation and prepares for sending",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to complete generation.

        Args:
            entity: The Report entity to complete
            **kwargs: Additional processing parameters

        Returns:
            The completed entity ready for sending
        """
        try:
            self.logger.info(
                f"Completing report generation for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Compile final summary data
            summary_data = report.compile_final_summary()

            # Set generated timestamp
            report.set_generated_at()

            # Set status to ready
            report.status = "ready"

            self.logger.info(
                f"Report generation completed for Report {report.technical_id} "
                f"(total comments: {report.total_comments}, avg sentiment: {report.avg_sentiment:.2f})"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error completing report generation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
