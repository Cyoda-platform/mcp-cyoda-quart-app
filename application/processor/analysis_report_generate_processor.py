"""
AnalysisReportGenerateProcessor for Cyoda Client Application

Finalizes the report generation.
"""

import logging
from typing import Any

from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class AnalysisReportGenerateProcessor(CyodaProcessor):
    """
    Processor for finalizing AnalysisReport generation.
    Validates all required fields are populated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportGenerateProcessor",
            description="Finalizes the report generation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Finalize the report generation according to functional requirements.

        Args:
            entity: The AnalysisReport with analysis data
            **kwargs: Additional processing parameters

        Returns:
            AnalysisReport ready for sending
        """
        try:
            self.logger.info(
                f"Finalizing report generation for AnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # Validate all required fields are populated
            if not report_entity.analysis_request_id:
                raise ValueError("Analysis request ID is required")

            if report_entity.total_comments < 0:
                raise ValueError("Total comments must be non-negative")

            if report_entity.average_comment_length < 0:
                raise ValueError("Average comment length must be non-negative")

            if not report_entity.most_active_email_domain:
                raise ValueError("Most active email domain is required")

            if not report_entity.sentiment_summary:
                raise ValueError("Sentiment summary is required")

            if not report_entity.top_keywords:
                raise ValueError("Top keywords are required")

            if not report_entity.generated_at:
                raise ValueError("Generated at timestamp is required")

            self.logger.info(
                f"AnalysisReport {report_entity.technical_id} generation finalized successfully"
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error finalizing report generation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
