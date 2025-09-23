"""
ReportValidationCriterion for Pet Store Performance Analysis System

Validates that a Report entity meets all required business rules before it can
proceed to the generation stage as specified in functional requirements.
"""

from datetime import datetime
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
            description="Validates Report business rules and data consistency for performance analysis",
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

            # Validate business logic
            if not self._validate_business_logic(report):
                return False

            # Validate email configuration
            if not self._validate_email_configuration(report):
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
        """
        Validate that all required fields are present and valid.

        Args:
            report: The Report entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate report title
        if not report.report_title or len(report.report_title.strip()) == 0:
            self.logger.warning(
                f"Report {report.technical_id} has invalid title: '{report.report_title}'"
            )
            return False

        if len(report.report_title) > 200:
            self.logger.warning(
                f"Report {report.technical_id} title too long: {len(report.report_title)} characters"
            )
            return False

        # Validate report type
        if report.report_type not in Report.ALLOWED_REPORT_TYPES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid type: {report.report_type}"
            )
            return False

        # Validate report period dates
        if not report.report_period_start or not report.report_period_end:
            self.logger.warning(
                f"Report {report.technical_id} missing period dates"
            )
            return False

        return True

    def _validate_business_logic(self, report: Report) -> bool:
        """
        Validate business logic rules.

        Args:
            report: The Report entity to validate

        Returns:
            True if business logic is valid, False otherwise
        """
        # Validate report period dates
        try:
            start_date = datetime.fromisoformat(report.report_period_start.replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(report.report_period_end.replace("Z", "+00:00"))
            
            if end_date <= start_date:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid period: end date must be after start date"
                )
                return False

            # Check if period is reasonable (not too long or too short)
            period_days = (end_date - start_date).days
            if period_days < 1:
                self.logger.warning(
                    f"Report {report.technical_id} period too short: {period_days} days"
                )
                return False
            
            if period_days > 365:  # More than a year
                self.logger.warning(
                    f"Report {report.technical_id} period too long: {period_days} days"
                )
                return False

        except ValueError as e:
            self.logger.warning(
                f"Report {report.technical_id} has invalid date format: {str(e)}"
            )
            return False

        # Validate email status
        if report.email_status not in Report.ALLOWED_EMAIL_STATUSES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid email status: {report.email_status}"
            )
            return False

        # Validate report format
        if report.report_format not in Report.ALLOWED_FORMATS:
            self.logger.warning(
                f"Report {report.technical_id} has invalid format: {report.report_format}"
            )
            return False

        # If email was sent, email_sent_at should be set
        if report.email_status == "SENT" and not report.email_sent_at:
            self.logger.warning(
                f"Report {report.technical_id} marked as sent but no sent timestamp"
            )
            return False

        return True

    def _validate_email_configuration(self, report: Report) -> bool:
        """
        Validate email configuration.

        Args:
            report: The Report entity to validate

        Returns:
            True if email configuration is valid, False otherwise
        """
        # Validate email recipients
        if not report.email_recipients or len(report.email_recipients) == 0:
            self.logger.warning(
                f"Report {report.technical_id} has no email recipients"
            )
            return False

        # Basic email validation
        for email in report.email_recipients:
            if not email or "@" not in email or "." not in email:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid email address: {email}"
                )
                return False

        # Ensure the required recipient is included
        required_recipient = "victoria.sagdieva@cyoda.com"
        if required_recipient not in report.email_recipients:
            self.logger.warning(
                f"Report {report.technical_id} missing required recipient: {required_recipient}"
            )
            return False

        return True
