"""
ReportValidationCriterion for Pet Store Performance Analysis System

Validates that a Report entity meets all required business rules before it can
proceed to email dispatch as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.report.version_1.report import Report


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks all business rules
    before the entity can proceed to email dispatch stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report completeness and data quality",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Report entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate required fields
            if not report.title or len(report.title.strip()) < 5:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid title: '{report.title}'"
                )
                return False

            if not report.report_type or report.report_type not in Report.ALLOWED_REPORT_TYPES:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid report type: {report.report_type}"
                )
                return False

            # Validate report periods
            if not report.report_period_start or not report.report_period_end:
                self.logger.warning(
                    f"Report {report.technical_id} missing report period dates"
                )
                return False

            # Validate executive summary exists and has content
            if not report.executive_summary or len(report.executive_summary.strip()) < 50:
                self.logger.warning(
                    f"Report {report.technical_id} has insufficient executive summary"
                )
                return False

            # Validate email recipients
            if not report.email_recipients or len(report.email_recipients) == 0:
                self.logger.warning(
                    f"Report {report.technical_id} has no email recipients"
                )
                return False

            # Validate email addresses format
            for email in report.email_recipients:
                if "@" not in email or "." not in email:
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid email: {email}"
                    )
                    return False

            # Validate analytics data is present
            if report.total_revenue is None or report.total_sales_volume is None:
                self.logger.warning(
                    f"Report {report.technical_id} missing analytics data"
                )
                return False

            # Validate generation timestamp
            if not report.generated_at:
                self.logger.warning(
                    f"Report {report.technical_id} missing generation timestamp"
                )
                return False

            # Business logic validation - ensure report has meaningful content
            has_content = (
                (report.top_performers and len(report.top_performers) > 0) or
                (report.underperformers and len(report.underperformers) > 0) or
                (report.restock_recommendations and len(report.restock_recommendations) > 0)
            )

            if not has_content:
                self.logger.warning(
                    f"Report {report.technical_id} has no meaningful content sections"
                )
                return False

            self.logger.info(
                f"Report {report.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Report entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
