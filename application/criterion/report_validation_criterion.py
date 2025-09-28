"""
ReportValidationCriterion for Cyoda Client Application

Validates that a CommentAnalysisReport entity meets all required business rules
before it can proceed to the report generation stage.
"""

from typing import Any

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for CommentAnalysisReport entity that checks all business rules
    before the entity can proceed to report generation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates CommentAnalysisReport business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the report meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be CommentAnalysisReport)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Validate required fields
            if not report.report_title or len(report.report_title.strip()) == 0:
                self.logger.warning(f"Report {report.technical_id} has empty title")
                return False

            if len(report.report_title) > 200:
                self.logger.warning(
                    f"Report {report.technical_id} title too long: {len(report.report_title)} characters"
                )
                return False

            # Validate email format
            if not report.recipient_email or "@" not in report.recipient_email:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid recipient email: {report.recipient_email}"
                )
                return False

            # Validate post_id is positive
            if report.post_id <= 0:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid post_id: {report.post_id}"
                )
                return False

            # Validate report hasn't already been emailed
            if report.email_sent:
                self.logger.warning(
                    f"Report {report.technical_id} has already been emailed"
                )
                return False

            self.logger.info(
                f"Report {report.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
