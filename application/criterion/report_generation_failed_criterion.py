"""
ReportGenerationFailedCriterion for Cyoda Client Application

Checks if report generation has failed.
Validates that report generation is incomplete as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ReportGenerationFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion for Report that checks if report generation has failed.
    Validates that summary data or generation timestamp is missing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationFailedCriterion",
            description="Checks if report generation has failed due to missing data or timestamps",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report entity generation has failed.

        Args:
            entity: The Report entity to check
            **kwargs: Additional parameters

        Returns:
            True if report generation has failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking report generation failure for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Check if summary data is missing or empty
            missing_summary = report.summary_data is None

            # Check if generated timestamp is missing
            missing_generated_at = report.generated_at is None

            has_failed = missing_summary or missing_generated_at

            self.logger.info(
                f"Report {report.technical_id} generation failure check: {has_failed} "
                f"(missing summary: {missing_summary}, missing generated_at: {missing_generated_at})"
            )

            return has_failed

        except Exception as e:
            self.logger.error(
                f"Error checking report generation failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return True  # Assume failure if we can't check properly
