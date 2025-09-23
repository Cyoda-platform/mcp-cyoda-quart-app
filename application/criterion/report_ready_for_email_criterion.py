"""
ReportReadyForEmailCriterion for Product Performance Analysis and Reporting System

Validates that a Report entity is ready to be emailed to the sales team
with all required content and metadata properly set.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity

from application.entity.report.version_1.report import Report


class ReportReadyForEmailCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Report entity to check if it's ready for email delivery.
    
    Ensures the report has all required content, metadata, and is in the correct state
    before attempting to send it via email.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportReadyForEmailCriterion",
            description="Validates that Report entity is ready for email delivery",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the report entity is ready for email delivery.

        Args:
            entity: The CyodaEntity to validate (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if the report is ready for email, False otherwise
        """
        try:
            self.logger.info(
                f"Validating report readiness for email {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report_entity = cast_entity(entity, Report)

            # Check if report has required content
            if not self._has_required_content(report_entity):
                self.logger.warning(
                    f"Report {report_entity.technical_id} missing required content"
                )
                return False

            # Check if report has valid metadata
            if not self._has_valid_metadata(report_entity):
                self.logger.warning(
                    f"Report {report_entity.technical_id} has invalid metadata"
                )
                return False

            # Check if email hasn't been sent already
            if report_entity.email_sent:
                self.logger.warning(
                    f"Report {report_entity.technical_id} has already been emailed"
                )
                return False

            # Check if report is in correct state
            if report_entity.state != "generated":
                self.logger.warning(
                    f"Report {report_entity.technical_id} is not in 'generated' state (current: {report_entity.state})"
                )
                return False

            # Check if email recipients are configured
            if not self._has_valid_recipients(report_entity):
                self.logger.warning(
                    f"Report {report_entity.technical_id} has no valid email recipients"
                )
                return False

            self.logger.info(
                f"Report {report_entity.technical_id} passed all email readiness criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating report readiness {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _has_required_content(self, report: Report) -> bool:
        """
        Check if report has all required content.

        Args:
            report: The Report entity to check

        Returns:
            True if report has required content, False otherwise
        """
        # Check for title
        if not report.title or len(report.title.strip()) == 0:
            self.logger.debug("Report missing title")
            return False

        # Check for main content
        if not report.content or len(report.content.strip()) == 0:
            self.logger.debug("Report missing main content")
            return False

        # Check for summary
        if not report.summary or len(report.summary.strip()) == 0:
            self.logger.debug("Report missing summary")
            return False

        # Check minimum content length
        if len(report.content) < 100:
            self.logger.debug("Report content too short")
            return False

        return True

    def _has_valid_metadata(self, report: Report) -> bool:
        """
        Check if report has valid metadata.

        Args:
            report: The Report entity to check

        Returns:
            True if report has valid metadata, False otherwise
        """
        # Check for report period
        if not report.report_period_start or not report.report_period_end:
            self.logger.debug("Report missing report period dates")
            return False

        # Check for generation timestamp
        if not report.generated_at:
            self.logger.debug("Report missing generation timestamp")
            return False

        # Check for email subject
        if not report.email_subject or len(report.email_subject.strip()) == 0:
            self.logger.debug("Report missing email subject")
            return False

        # Check for products analyzed count
        if report.total_products_analyzed is None or report.total_products_analyzed < 0:
            self.logger.debug("Report has invalid products analyzed count")
            return False

        return True

    def _has_valid_recipients(self, report: Report) -> bool:
        """
        Check if report has valid email recipients.

        Args:
            report: The Report entity to check

        Returns:
            True if report has valid recipients, False otherwise
        """
        # Check if recipients list exists and is not empty
        if not report.email_recipients or len(report.email_recipients) == 0:
            self.logger.debug("Report has no email recipients")
            return False

        # Validate each email address
        for email in report.email_recipients:
            if not self._is_valid_email(email):
                self.logger.debug(f"Invalid email address: {email}")
                return False

        return True

    def _is_valid_email(self, email: str) -> bool:
        """
        Basic email validation.

        Args:
            email: Email address to validate

        Returns:
            True if email appears valid, False otherwise
        """
        if not email or len(email.strip()) == 0:
            return False

        email = email.strip()

        # Basic email format validation
        if "@" not in email:
            return False

        if "." not in email:
            return False

        # Check for minimum length
        if len(email) < 5:
            return False

        # Check for valid characters (basic check)
        if email.startswith("@") or email.endswith("@"):
            return False

        if email.startswith(".") or email.endswith("."):
            return False

        return True
