"""
ReportValidationCriterion for Pet Store Performance Analysis System

Validates that a Report entity meets all required business rules before
it can proceed to the email delivery stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.report.version_1.report import Report


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks all business rules
    before the entity can proceed to email delivery stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report business rules and content completeness",
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
            if not report.title or len(report.title.strip()) < 1:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid title: '{report.title}'"
                )
                return False

            if not report.period_start:
                self.logger.warning(
                    f"Report {report.technical_id} missing period start date"
                )
                return False

            if not report.period_end:
                self.logger.warning(
                    f"Report {report.technical_id} missing period end date"
                )
                return False

            # Validate report type
            if report.report_type not in Report.ALLOWED_REPORT_TYPES:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid report type: {report.report_type}"
                )
                return False

            # Validate email recipient
            if not report.email_recipient or "@" not in report.email_recipient:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid email recipient: {report.email_recipient}"
                )
                return False

            # Validate numeric fields
            if report.total_products_analyzed is not None and report.total_products_analyzed < 0:
                self.logger.warning(
                    f"Report {report.technical_id} has negative products count: {report.total_products_analyzed}"
                )
                return False

            if report.total_revenue is not None and report.total_revenue < 0:
                self.logger.warning(
                    f"Report {report.technical_id} has negative revenue: {report.total_revenue}"
                )
                return False

            # Validate report content completeness
            if not report.executive_summary or len(report.executive_summary.strip()) < 10:
                self.logger.warning(
                    f"Report {report.technical_id} has insufficient executive summary"
                )
                return False

            if not report.generated_at:
                self.logger.warning(
                    f"Report {report.technical_id} missing generation timestamp"
                )
                return False

            # Business logic validation
            # Report should have been generated before validation
            if report.total_products_analyzed == 0:
                self.logger.warning(
                    f"Report {report.technical_id} has no products analyzed - may be empty report"
                )
                # This is a warning but not a failure - empty reports can be valid

            # Validate period dates make sense
            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(report.period_start.replace("Z", "+00:00"))
                end_date = datetime.fromisoformat(report.period_end.replace("Z", "+00:00"))
                
                if start_date >= end_date:
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid date range: start >= end"
                    )
                    return False
                    
                # Check if period is reasonable (not too long)
                period_days = (end_date - start_date).days
                if period_days > 90:  # More than 3 months
                    self.logger.warning(
                        f"Report {report.technical_id} has unusually long period: {period_days} days"
                    )
                    return False
                    
            except Exception as e:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid date format: {str(e)}"
                )
                return False

            # Validate that report hasn't already been emailed
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
                f"Error validating Report entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
