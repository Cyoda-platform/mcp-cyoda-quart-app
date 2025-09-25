"""
ReportValidationCriterion for Pet Store Performance Analysis System

Validates that a Report entity meets all required business rules before it can
proceed to report generation stage as specified in functional requirements.
"""

from typing import Any

from application.entity.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ReportValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity that checks all business rules
    before the entity can proceed to report generation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportValidationCriterion",
            description="Validates Report business rules and data consistency",
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

            # Validate field constraints
            if not self._validate_field_constraints(report):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(report):
                return False

            # Validate data period consistency
            if not self._validate_data_period(report):
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
        Validate that all required fields are present and non-empty.

        Args:
            report: The Report entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate report title
        if not report.title or len(report.title.strip()) == 0:
            self.logger.warning(
                f"Report {report.technical_id} has empty or missing title"
            )
            return False

        if len(report.title.strip()) < 5:
            self.logger.warning(
                f"Report {report.technical_id} title too short: '{report.title}'"
            )
            return False

        if len(report.title) > 200:
            self.logger.warning(
                f"Report {report.technical_id} title too long: {len(report.title)} characters"
            )
            return False

        # Validate report type
        if not report.report_type:
            self.logger.warning(f"Report {report.technical_id} has missing report type")
            return False

        if report.report_type not in report.ALLOWED_REPORT_TYPES:
            self.logger.warning(
                f"Report {report.technical_id} has invalid report type: {report.report_type}"
            )
            return False

        return True

    def _validate_field_constraints(self, report: Report) -> bool:
        """
        Validate field constraints and data types.

        Args:
            report: The Report entity to validate

        Returns:
            True if all field constraints are met, False otherwise
        """
        # Validate content length if present
        if report.content is not None and len(report.content) > 50000:
            self.logger.warning(
                f"Report {report.technical_id} content too long: {len(report.content)} characters"
            )
            return False

        # Validate email recipients format if present
        if report.email_recipients:
            for email in report.email_recipients:
                if not email or "@" not in email or "." not in email.split("@")[-1]:
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid email recipient: {email}"
                    )
                    return False

        # Validate generated_by field
        if report.generated_by and len(report.generated_by) > 100:
            self.logger.warning(
                f"Report {report.technical_id} generated_by field too long"
            )
            return False

        return True

    def _validate_business_rules(self, report: Report) -> bool:
        """
        Validate business logic rules specific to the reporting domain.

        Args:
            report: The Report entity to validate

        Returns:
            True if all business rules are met, False otherwise
        """
        # Validate email consistency
        if report.email_sent and not report.emailed_at:
            self.logger.warning(
                f"Report {report.technical_id} marked as emailed but missing emailed_at timestamp"
            )
            return False

        if report.emailed_at and not report.email_sent:
            self.logger.warning(
                f"Report {report.technical_id} has emailed_at timestamp but email_sent is False"
            )
            return False

        # Validate report type specific rules
        if not self._validate_report_type_rules(report):
            return False

        # Validate content consistency
        if not self._validate_content_consistency(report):
            return False

        return True

    def _validate_report_type_rules(self, report: Report) -> bool:
        """
        Validate rules specific to different report types.

        Args:
            report: The Report entity to validate

        Returns:
            True if report type specific rules are met, False otherwise
        """
        report_type = report.report_type

        # Weekly summary reports should have appropriate data period
        if report_type == "WEEKLY_SUMMARY":
            if report.data_period_start and report.data_period_end:
                try:
                    from datetime import datetime, timedelta

                    start_date = datetime.fromisoformat(
                        report.data_period_start.replace("Z", "+00:00")
                    )
                    end_date = datetime.fromisoformat(
                        report.data_period_end.replace("Z", "+00:00")
                    )
                    period_length = end_date - start_date

                    # Weekly reports should cover approximately 7 days
                    if period_length.days < 6 or period_length.days > 8:
                        self.logger.warning(
                            f"Weekly report {report.technical_id} has unusual period length: {period_length.days} days"
                        )
                        # This is a warning, not a validation failure

                except ValueError:
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid date format in data period"
                    )
                    return False

        # Monthly analysis reports should have appropriate data period
        elif report_type == "MONTHLY_ANALYSIS":
            if report.data_period_start and report.data_period_end:
                try:
                    from datetime import datetime

                    start_date = datetime.fromisoformat(
                        report.data_period_start.replace("Z", "+00:00")
                    )
                    end_date = datetime.fromisoformat(
                        report.data_period_end.replace("Z", "+00:00")
                    )
                    period_length = end_date - start_date

                    # Monthly reports should cover approximately 30 days
                    if period_length.days < 28 or period_length.days > 32:
                        self.logger.warning(
                            f"Monthly report {report.technical_id} has unusual period length: {period_length.days} days"
                        )
                        # This is a warning, not a validation failure

                except ValueError:
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid date format in data period"
                    )
                    return False

        # Performance analysis reports should have insights
        elif report_type == "PERFORMANCE_ANALYSIS":
            if report.insights is None or len(report.insights) == 0:
                self.logger.info(
                    f"Performance analysis report {report.technical_id} has no insights yet (will be generated)"
                )
                # This is informational - insights will be generated during processing

        return True

    def _validate_data_period(self, report: Report) -> bool:
        """
        Validate data period consistency and logic.

        Args:
            report: The Report entity to validate

        Returns:
            True if data period is valid, False otherwise
        """
        if report.data_period_start and report.data_period_end:
            try:
                from datetime import datetime, timezone

                start_date = datetime.fromisoformat(
                    report.data_period_start.replace("Z", "+00:00")
                )
                end_date = datetime.fromisoformat(
                    report.data_period_end.replace("Z", "+00:00")
                )
                current_time = datetime.now(timezone.utc)

                # Start date should be before end date
                if start_date >= end_date:
                    self.logger.warning(
                        f"Report {report.technical_id} has start date after or equal to end date"
                    )
                    return False

                # End date should not be too far in the future
                if end_date > current_time:
                    future_days = (end_date - current_time).days
                    if (
                        future_days > 1
                    ):  # Allow 1 day tolerance for timezone differences
                        self.logger.warning(
                            f"Report {report.technical_id} has end date too far in future: {future_days} days"
                        )
                        return False

                # Data period should not be too long (max 1 year)
                period_length = end_date - start_date
                if period_length.days > 365:
                    self.logger.warning(
                        f"Report {report.technical_id} has data period too long: {period_length.days} days"
                    )
                    return False

                # Data period should not be too short (min 1 day)
                if period_length.total_seconds() < 86400:  # 24 hours
                    self.logger.warning(
                        f"Report {report.technical_id} has data period too short: {period_length.total_seconds()} seconds"
                    )
                    return False

            except ValueError as e:
                self.logger.warning(
                    f"Report {report.technical_id} has invalid date format in data period: {str(e)}"
                )
                return False

        return True

    def _validate_content_consistency(self, report: Report) -> bool:
        """
        Validate consistency between content and metadata.

        Args:
            report: The Report entity to validate

        Returns:
            True if content is consistent, False otherwise
        """
        # If report has been generated, it should have content
        if report.generated_at and (
            not report.content or len(report.content.strip()) == 0
        ):
            self.logger.warning(
                f"Report {report.technical_id} marked as generated but has no content"
            )
            return False

        # If report has insights, they should be reasonable
        if report.insights:
            if not isinstance(report.insights, dict):
                self.logger.warning(
                    f"Report {report.technical_id} has insights that are not a dictionary"
                )
                return False

            # Check for required insight fields
            expected_fields = [
                "total_products_analyzed",
                "total_revenue",
                "average_performance_score",
            ]
            for field in expected_fields:
                if field in report.insights:
                    value = report.insights[field]
                    if not isinstance(value, (int, float)) or value < 0:
                        self.logger.warning(
                            f"Report {report.technical_id} has invalid insight value for {field}: {value}"
                        )
                        # This is a warning, not a validation failure

        # If report has summary metrics, validate them
        if report.summary_metrics:
            if not isinstance(report.summary_metrics, dict):
                self.logger.warning(
                    f"Report {report.technical_id} has summary_metrics that are not a dictionary"
                )
                return False

        # If report has product highlights, validate them
        if report.product_highlights:
            if not isinstance(report.product_highlights, list):
                self.logger.warning(
                    f"Report {report.technical_id} has product_highlights that are not a list"
                )
                return False

            for i, highlight in enumerate(report.product_highlights):
                if not isinstance(highlight, dict):
                    self.logger.warning(
                        f"Report {report.technical_id} has invalid product highlight at index {i}"
                    )
                    return False

        return True

    def _validate_email_configuration(self, report: Report) -> bool:
        """
        Validate email configuration for the report.

        Args:
            report: The Report entity to validate

        Returns:
            True if email configuration is valid, False otherwise
        """
        # Check if email recipients are configured for reports that should be emailed
        if report.report_type in ["WEEKLY_SUMMARY", "MONTHLY_ANALYSIS"]:
            if not report.email_recipients or len(report.email_recipients) == 0:
                self.logger.info(
                    f"Report {report.technical_id} of type {report.report_type} has no email recipients configured"
                )
                # This is informational - recipients will be set during processing

        # Validate that victoria.sagdieva@cyoda.com is included for weekly reports
        if report.report_type == "WEEKLY_SUMMARY" and report.email_recipients:
            required_recipient = "victoria.sagdieva@cyoda.com"
            if required_recipient not in report.email_recipients:
                self.logger.warning(
                    f"Weekly report {report.technical_id} missing required recipient: {required_recipient}"
                )
                # This is a warning - the processor will add the required recipient

        return True
