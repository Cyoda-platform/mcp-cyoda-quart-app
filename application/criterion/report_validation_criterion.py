"""
ReportValidationCriterion for Product Performance Analysis and Reporting System

Validates Report entities to ensure proper report configuration and data integrity
before proceeding to report generation.
"""

from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks report configuration and data integrity.

    Validates:
    - Required report metadata
    - Date range validity
    - Email configuration
    - Report type and settings
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report entity configuration and data integrity",
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

            # Validate date ranges
            if not self._validate_date_ranges(report):
                return False

            # Validate email configuration
            if not self._validate_email_configuration(report):
                return False

            # Validate report settings
            if not self._validate_report_settings(report):
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
        # Validate title
        if not report.title or len(report.title.strip()) == 0:
            self.logger.warning(
                f"Report {report.technical_id} has invalid title: '{report.title}'"
            )
            return False

        if len(report.title) > 200:
            self.logger.warning(
                f"Report {report.technical_id} title too long: {len(report.title)} characters"
            )
            return False

        # Validate report type
        if (
            not report.report_type
            or report.report_type not in report.ALLOWED_REPORT_TYPES
        ):
            self.logger.warning(
                f"Report {report.technical_id} has invalid report type: '{report.report_type}'"
            )
            return False

        # Validate period dates
        if not report.period_start or not report.period_end:
            self.logger.warning(f"Report {report.technical_id} missing period dates")
            return False

        # Validate summary
        if not report.summary or len(report.summary.strip()) == 0:
            self.logger.warning(f"Report {report.technical_id} has empty summary")
            return False

        return True

    def _validate_date_ranges(self, report: Report) -> bool:
        """
        Validate date ranges and timestamp formats.

        Args:
            report: The Report entity to validate

        Returns:
            True if all date ranges are valid, False otherwise
        """
        try:
            from datetime import datetime

            # Parse period dates
            start_date = datetime.fromisoformat(
                report.period_start.replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(report.period_end.replace("Z", "+00:00"))

            # Validate date range logic
            if start_date >= end_date:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid date range: "
                    f"start {report.period_start} >= end {report.period_end}"
                )
                return False

            # Validate reasonable date range (not too far in past/future)
            now = datetime.now(start_date.tzinfo)
            days_diff = (end_date - start_date).days

            if days_diff > 365:  # More than a year
                self.logger.warning(
                    f"Report {report.technical_id} has unrealistic date range: {days_diff} days"
                )
                return False

            if start_date > now:
                self.logger.warning(
                    f"Report {report.technical_id} has future start date: {report.period_start}"
                )
                return False

            # Validate other timestamps if present
            timestamp_fields = [
                report.generated_at,
                report.email_sent_at,
                report.created_at,
                report.updated_at,
            ]

            for timestamp in timestamp_fields:
                if timestamp is not None:
                    if not self._validate_timestamp_format(timestamp):
                        self.logger.warning(
                            f"Report {report.technical_id} has invalid timestamp format: {timestamp}"
                        )
                        return False

            return True

        except (ValueError, AttributeError) as e:
            self.logger.warning(
                f"Report {report.technical_id} has invalid date format: {str(e)}"
            )
            return False

    def _validate_email_configuration(self, report: Report) -> bool:
        """
        Validate email configuration and recipients.

        Args:
            report: The Report entity to validate

        Returns:
            True if email configuration is valid, False otherwise
        """
        # Validate email recipients
        if not report.email_recipients or len(report.email_recipients) == 0:
            self.logger.warning(f"Report {report.technical_id} has no email recipients")
            return False

        # Validate email addresses format
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        for email in report.email_recipients:
            if not re.match(email_pattern, email):
                self.logger.warning(
                    f"Report {report.technical_id} has invalid email address: {email}"
                )
                return False

        # Validate email status
        if report.email_status not in report.ALLOWED_EMAIL_STATUSES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid email status: {report.email_status}"
            )
            return False

        # Validate generated_by field
        if not report.generated_by or len(report.generated_by.strip()) == 0:
            self.logger.warning(
                f"Report {report.technical_id} has empty generated_by field"
            )
            return False

        return True

    def _validate_report_settings(self, report: Report) -> bool:
        """
        Validate report settings and configuration.

        Args:
            report: The Report entity to validate

        Returns:
            True if report settings are valid, False otherwise
        """
        # Validate total products analyzed
        if report.total_products_analyzed < 0:
            self.logger.warning(
                f"Report {report.technical_id} has negative total products: {report.total_products_analyzed}"
            )
            return False

        # Validate revenue values
        if report.total_revenue is not None and report.total_revenue < 0:
            self.logger.warning(
                f"Report {report.technical_id} has negative total revenue: {report.total_revenue}"
            )
            return False

        # Validate performance score
        if report.average_performance_score is not None and (
            report.average_performance_score < 0
            or report.average_performance_score > 100
        ):
            self.logger.warning(
                f"Report {report.technical_id} has invalid average performance score: {report.average_performance_score}"
            )
            return False

        # Validate growth percentage (reasonable range)
        if report.revenue_growth_percentage is not None and (
            report.revenue_growth_percentage < -100
            or report.revenue_growth_percentage > 1000
        ):
            self.logger.warning(
                f"Report {report.technical_id} has unrealistic growth percentage: {report.revenue_growth_percentage}"
            )
            return False

        # Validate file information if present
        if report.file_path is not None:
            if len(report.file_path.strip()) == 0:
                self.logger.warning(f"Report {report.technical_id} has empty file path")
                return False

        if report.file_size is not None and report.file_size < 0:
            self.logger.warning(
                f"Report {report.technical_id} has negative file size: {report.file_size}"
            )
            return False

        # Validate data extraction reference if present
        if report.data_extraction_id is not None:
            if len(str(report.data_extraction_id).strip()) == 0:
                self.logger.warning(
                    f"Report {report.technical_id} has empty data extraction ID"
                )
                return False

        return True

    def _validate_timestamp_format(self, timestamp: str) -> bool:
        """
        Validate ISO 8601 timestamp format.

        Args:
            timestamp: Timestamp string to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            from datetime import datetime

            # Try to parse ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False
