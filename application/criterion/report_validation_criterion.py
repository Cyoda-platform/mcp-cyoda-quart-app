"""
ReportValidationCriterion for Product Performance Analysis and Reporting System

Validates that a Report entity meets all required business rules before it can
proceed to the report generation stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.report.version_1.report import Report


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks all business rules
    before the entity can proceed to report generation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report entity business rules and data consistency",
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
            if not self._validate_required_fields(report):
                return False

            # Validate field formats and constraints
            if not self._validate_field_constraints(report):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(report):
                return False

            self.logger.info(
                f"Report entity {report.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Report entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, report: Report) -> bool:
        """Validate that all required fields are present and valid"""
        
        # Report title is required
        if not report.report_title or len(report.report_title.strip()) == 0:
            self.logger.warning(f"Report {report.technical_id} has empty report title")
            return False

        if len(report.report_title) > 255:
            self.logger.warning(f"Report {report.technical_id} title too long: {len(report.report_title)} characters")
            return False

        # Report type is required
        if not report.report_type:
            self.logger.warning(f"Report {report.technical_id} has no report type")
            return False

        # Report period is required
        if not report.report_period or len(report.report_period.strip()) == 0:
            self.logger.warning(f"Report {report.technical_id} has empty report period")
            return False

        # Email recipient is required
        if not report.email_recipient or len(report.email_recipient.strip()) == 0:
            self.logger.warning(f"Report {report.technical_id} has empty email recipient")
            return False

        return True

    def _validate_field_constraints(self, report: Report) -> bool:
        """Validate field formats and constraints"""
        
        # Validate report type
        if report.report_type not in Report.VALID_REPORT_TYPES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid report type: {report.report_type}. "
                f"Valid types: {Report.VALID_REPORT_TYPES}"
            )
            return False

        # Validate email recipient format
        if "@" not in report.email_recipient or "." not in report.email_recipient:
            self.logger.warning(f"Report {report.technical_id} has invalid email format: {report.email_recipient}")
            return False

        # Validate email status if present
        if report.email_status and report.email_status not in Report.VALID_EMAIL_STATUSES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid email status: {report.email_status}. "
                f"Valid statuses: {Report.VALID_EMAIL_STATUSES}"
            )
            return False

        # Validate performance score if present
        if report.performance_score is not None:
            if report.performance_score < 0.0 or report.performance_score > 100.0:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid performance score: {report.performance_score}. "
                    "Must be between 0.0 and 100.0"
                )
                return False

        # Validate numeric fields if present
        for field_name, field_value in [
            ("total_pets_analyzed", report.total_pets_analyzed),
            ("stores_analyzed", report.stores_analyzed),
        ]:
            if field_value is not None and (not isinstance(field_value, int) or field_value < 0):
                self.logger.warning(
                    f"Report {report.technical_id} has invalid {field_name}: {field_value}"
                )
                return False

        return True

    def _validate_business_rules(self, report: Report) -> bool:
        """Validate business logic rules"""
        
        # Business rule: Weekly reports should be sent to victoria.sagdieva@cyoda.com as per requirements
        if report.report_type == "weekly" and report.email_recipient != "victoria.sagdieva@cyoda.com":
            self.logger.warning(
                f"Report {report.technical_id} is a weekly report but recipient is not victoria.sagdieva@cyoda.com: "
                f"{report.email_recipient}"
            )
            # This is a warning, not a failure - allow other recipients for testing

        # Business rule: Report period should be reasonable format
        if not self._validate_report_period_format(report.report_period):
            self.logger.warning(
                f"Report {report.technical_id} has unusual report period format: {report.report_period}"
            )
            # This is a warning, not a failure - allow flexible formats

        # Business rule: If report is already generated, it should have data
        if report.generated_at and not report.report_data:
            self.logger.warning(
                f"Report {report.technical_id} is marked as generated but has no report data"
            )
            return False

        # Business rule: If email is marked as sent, it should have sent timestamp
        if report.email_status == "sent" and not report.email_sent_at:
            self.logger.warning(
                f"Report {report.technical_id} is marked as sent but has no sent timestamp"
            )
            return False

        return True

    def _validate_report_period_format(self, period: str) -> bool:
        """Validate report period format (flexible validation)"""
        # Accept various formats like:
        # - "2024-01-01 to 2024-01-07"
        # - "Week of 2024-01-01"
        # - "January 2024"
        # - "Q1 2024"
        
        if len(period) < 5:  # Too short to be meaningful
            return False
        
        # Check for common date patterns or keywords
        common_patterns = [
            "to", "week", "month", "quarter", "q1", "q2", "q3", "q4",
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
            "2024", "2023", "2025"  # Common years
        ]
        
        period_lower = period.lower()
        return any(pattern in period_lower for pattern in common_patterns)
