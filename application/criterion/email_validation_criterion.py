"""
EmailValidationCriterion for Pet Store Performance Analysis System

Validates that an EmailNotification entity meets all required business rules before it can
proceed to email dispatch stage as specified in functional requirements.
"""

from typing import Any

from application.entity.email_notification import EmailNotification
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class EmailValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for EmailNotification entity that checks all business rules
    before the entity can proceed to email dispatch stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailValidationCriterion",
            description="Validates EmailNotification business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the EmailNotification entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be EmailNotification)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating EmailNotification entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            email_notification = cast_entity(entity, EmailNotification)

            # Validate required fields
            if not self._validate_required_fields(email_notification):
                return False

            # Validate email format and constraints
            if not self._validate_email_format(email_notification):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(email_notification):
                return False

            # Validate delivery constraints
            if not self._validate_delivery_constraints(email_notification):
                return False

            self.logger.info(
                f"EmailNotification entity {email_notification.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating EmailNotification entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, email_notification: EmailNotification) -> bool:
        """
        Validate that all required fields are present and non-empty.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate recipient email
        if (
            not email_notification.recipient_email
            or len(email_notification.recipient_email.strip()) == 0
        ):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has empty or missing recipient email"
            )
            return False

        # Validate subject
        if (
            not email_notification.subject
            or len(email_notification.subject.strip()) == 0
        ):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has empty or missing subject"
            )
            return False

        if len(email_notification.subject) > 200:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} subject too long: {len(email_notification.subject)} characters"
            )
            return False

        # Validate email type
        if not email_notification.email_type:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has missing email type"
            )
            return False

        if email_notification.email_type not in email_notification.ALLOWED_EMAIL_TYPES:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has invalid email type: {email_notification.email_type}"
            )
            return False

        # Validate priority
        if not email_notification.priority:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has missing priority"
            )
            return False

        if email_notification.priority not in email_notification.ALLOWED_PRIORITIES:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has invalid priority: {email_notification.priority}"
            )
            return False

        # Validate status
        if not email_notification.status:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has missing status"
            )
            return False

        if email_notification.status not in email_notification.ALLOWED_STATUSES:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has invalid status: {email_notification.status}"
            )
            return False

        return True

    def _validate_email_format(self, email_notification: EmailNotification) -> bool:
        """
        Validate email address formats and constraints.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if email formats are valid, False otherwise
        """
        # Validate recipient email format
        recipient_email = email_notification.recipient_email
        if not self._is_valid_email_format(recipient_email):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has invalid recipient email format: {recipient_email}"
            )
            return False

        # Validate sender email format if present
        if email_notification.sender_email:
            if not self._is_valid_email_format(email_notification.sender_email):
                self.logger.warning(
                    f"EmailNotification {email_notification.technical_id} has invalid sender email format: {email_notification.sender_email}"
                )
                return False

        # Validate content length if present
        if (
            email_notification.content is not None
            and len(email_notification.content) > 100000
        ):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} content too long: {len(email_notification.content)} characters"
            )
            return False

        return True

    def _validate_business_rules(self, email_notification: EmailNotification) -> bool:
        """
        Validate business logic rules specific to email notifications.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if all business rules are met, False otherwise
        """
        # Validate status consistency with timestamps
        if email_notification.status == "SENT" and not email_notification.sent_at:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} status is SENT but missing sent_at timestamp"
            )
            return False

        if (
            email_notification.status == "DELIVERED"
            and not email_notification.delivered_at
        ):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} status is DELIVERED but missing delivered_at timestamp"
            )
            return False

        if (
            email_notification.status == "FAILED"
            and email_notification.delivery_attempts == 0
        ):
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} status is FAILED but no delivery attempts recorded"
            )
            return False

        # Validate delivery attempts
        if email_notification.delivery_attempts < 0:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has negative delivery attempts: {email_notification.delivery_attempts}"
            )
            return False

        if email_notification.delivery_attempts > 10:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has too many delivery attempts: {email_notification.delivery_attempts}"
            )
            return False

        # Validate timestamp consistency
        if not self._validate_timestamp_consistency(email_notification):
            return False

        # Validate email type specific rules
        if not self._validate_email_type_rules(email_notification):
            return False

        return True

    def _validate_delivery_constraints(
        self, email_notification: EmailNotification
    ) -> bool:
        """
        Validate delivery constraints and readiness.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if delivery constraints are met, False otherwise
        """
        # Check if email is ready to send
        if email_notification.status == "PENDING":
            if (
                not email_notification.content
                or len(email_notification.content.strip()) == 0
            ):
                self.logger.warning(
                    f"EmailNotification {email_notification.technical_id} is pending but has no content"
                )
                return False

        # Validate retry constraints
        if email_notification.status == "FAILED":
            if email_notification.delivery_attempts >= 3:
                self.logger.info(
                    f"EmailNotification {email_notification.technical_id} has exceeded retry limit"
                )
                # This is informational - the email should not be retried

        # Validate scheduled delivery
        if email_notification.scheduled_at:
            try:
                from datetime import datetime, timezone

                scheduled_time = datetime.fromisoformat(
                    email_notification.scheduled_at.replace("Z", "+00:00")
                )
                current_time = datetime.now(timezone.utc)

                # Scheduled time should not be too far in the past
                time_diff = current_time - scheduled_time
                if time_diff.total_seconds() > 86400:  # 24 hours
                    self.logger.warning(
                        f"EmailNotification {email_notification.technical_id} scheduled time is too far in the past"
                    )
                    # This is a warning, not a validation failure

            except ValueError:
                self.logger.warning(
                    f"EmailNotification {email_notification.technical_id} has invalid scheduled_at timestamp format"
                )
                return False

        return True

    def _validate_email_type_rules(self, email_notification: EmailNotification) -> bool:
        """
        Validate rules specific to different email types.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if email type specific rules are met, False otherwise
        """
        email_type = email_notification.email_type

        # Weekly report emails should go to victoria.sagdieva@cyoda.com
        if email_type == "WEEKLY_REPORT":
            required_recipient = "victoria.sagdieva@cyoda.com"
            if email_notification.recipient_email != required_recipient:
                self.logger.warning(
                    f"Weekly report email {email_notification.technical_id} should be sent to {required_recipient}, "
                    f"but recipient is {email_notification.recipient_email}"
                )
                return False

        # Report notifications should have associated report ID
        if email_type in ["REPORT_NOTIFICATION", "WEEKLY_REPORT", "MONTHLY_REPORT"]:
            if not email_notification.report_id:
                self.logger.warning(
                    f"Report email {email_notification.technical_id} missing report_id"
                )
                return False

        # Alert emails should have high priority
        if email_type == "ALERT":
            if email_notification.priority not in ["HIGH", "URGENT"]:
                self.logger.warning(
                    f"Alert email {email_notification.technical_id} should have HIGH or URGENT priority, "
                    f"but priority is {email_notification.priority}"
                )
                # This is a warning, not a validation failure

        return True

    def _validate_timestamp_consistency(
        self, email_notification: EmailNotification
    ) -> bool:
        """
        Validate timestamp consistency and logic.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if timestamps are consistent, False otherwise
        """
        try:
            from datetime import datetime, timezone

            current_time = datetime.now(timezone.utc)

            # Validate sent_at timestamp
            if email_notification.sent_at:
                sent_time = datetime.fromisoformat(
                    email_notification.sent_at.replace("Z", "+00:00")
                )

                # Sent time should not be in the future
                if sent_time > current_time:
                    self.logger.warning(
                        f"EmailNotification {email_notification.technical_id} has future sent_at timestamp"
                    )
                    return False

            # Validate delivered_at timestamp
            if email_notification.delivered_at:
                delivered_time = datetime.fromisoformat(
                    email_notification.delivered_at.replace("Z", "+00:00")
                )

                # Delivered time should not be in the future
                if delivered_time > current_time:
                    self.logger.warning(
                        f"EmailNotification {email_notification.technical_id} has future delivered_at timestamp"
                    )
                    return False

            # Validate timestamp order
            if email_notification.sent_at and email_notification.delivered_at:
                sent_time = datetime.fromisoformat(
                    email_notification.sent_at.replace("Z", "+00:00")
                )
                delivered_time = datetime.fromisoformat(
                    email_notification.delivered_at.replace("Z", "+00:00")
                )

                if sent_time > delivered_time:
                    self.logger.warning(
                        f"EmailNotification {email_notification.technical_id} has sent_at after delivered_at"
                    )
                    return False

        except ValueError as e:
            self.logger.warning(
                f"EmailNotification {email_notification.technical_id} has invalid timestamp format: {str(e)}"
            )
            return False

        return True

    def _is_valid_email_format(self, email: str) -> bool:
        """
        Check if email address has valid format.

        Args:
            email: Email address to validate

        Returns:
            True if email format is valid, False otherwise
        """
        if not email or len(email.strip()) == 0:
            return False

        # Basic email format validation
        if "@" not in email:
            return False

        local_part, domain_part = email.rsplit("@", 1)

        # Validate local part
        if len(local_part) == 0 or len(local_part) > 64:
            return False

        # Validate domain part
        if len(domain_part) == 0 or len(domain_part) > 253:
            return False

        if "." not in domain_part:
            return False

        # Check for valid characters (basic check)
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_+"
        )
        if not all(c in valid_chars for c in email):
            return False

        # Email should not be too long (RFC 5321 limit)
        if len(email) > 254:
            return False

        return True

    def _validate_content_requirements(
        self, email_notification: EmailNotification
    ) -> bool:
        """
        Validate content requirements based on email type.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if content requirements are met, False otherwise
        """
        # Report emails should have substantial content
        if email_notification.email_type in [
            "REPORT_NOTIFICATION",
            "WEEKLY_REPORT",
            "MONTHLY_REPORT",
        ]:
            if (
                email_notification.content
                and len(email_notification.content.strip()) < 100
            ):
                self.logger.warning(
                    f"Report email {email_notification.technical_id} has very short content: {len(email_notification.content)} characters"
                )
                # This is a warning, not a validation failure

        # Alert emails should have clear subject lines
        if email_notification.email_type == "ALERT":
            alert_keywords = ["alert", "urgent", "warning", "critical", "attention"]
            subject_lower = email_notification.subject.lower()
            if not any(keyword in subject_lower for keyword in alert_keywords):
                self.logger.warning(
                    f"Alert email {email_notification.technical_id} subject may not clearly indicate alert: {email_notification.subject}"
                )
                # This is a warning, not a validation failure

        return True
