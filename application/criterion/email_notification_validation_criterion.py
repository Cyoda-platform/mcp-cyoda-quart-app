"""
EmailNotificationValidationCriterion for Product Performance Analysis System

Validates EmailNotification entities for email format and delivery requirements
before email preparation as specified in functional requirements.
"""

import re
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity

from application.entity.email_notification.version_1.email_notification import EmailNotification


class EmailNotificationValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for EmailNotification entities.
    
    Checks email format, recipient validity, and delivery requirements before
    allowing EmailNotification entities to proceed to email preparation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailNotificationValidationCriterion",
            description="Validates EmailNotification entities for email format and delivery requirements",
        )
        # Email validation regex pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

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

            # Validate email addresses
            if not self._validate_email_addresses(email_notification):
                return False

            # Validate field constraints
            if not self._validate_field_constraints(email_notification):
                return False

            # Validate business rules
            if not self._validate_business_rules(email_notification):
                return False

            self.logger.info(
                f"EmailNotification entity {email_notification.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
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
        # Validate subject
        if not email_notification.subject or len(email_notification.subject.strip()) == 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid subject: '{email_notification.subject}'"
            )
            return False

        # Validate recipient_email
        if not email_notification.recipient_email or len(email_notification.recipient_email.strip()) == 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid recipient_email: '{email_notification.recipient_email}'"
            )
            return False

        # Validate email_body
        if not email_notification.email_body or len(email_notification.email_body.strip()) == 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid email_body: '{email_notification.email_body}'"
            )
            return False

        return True

    def _validate_email_addresses(self, email_notification: EmailNotification) -> bool:
        """
        Validate email address formats.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if all email addresses are valid, False otherwise
        """
        # Validate primary recipient
        if not self._is_valid_email(email_notification.recipient_email):
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid recipient_email format: "
                f"'{email_notification.recipient_email}'"
            )
            return False

        # Validate CC recipients
        for cc_email in email_notification.cc_recipients:
            if not self._is_valid_email(cc_email):
                self.logger.warning(
                    f"Entity {email_notification.technical_id} has invalid CC email format: '{cc_email}'"
                )
                return False

        # Validate BCC recipients
        for bcc_email in email_notification.bcc_recipients:
            if not self._is_valid_email(bcc_email):
                self.logger.warning(
                    f"Entity {email_notification.technical_id} has invalid BCC email format: '{bcc_email}'"
                )
                return False

        return True

    def _validate_field_constraints(self, email_notification: EmailNotification) -> bool:
        """
        Validate field constraints and formats.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if all field constraints are met, False otherwise
        """
        # Validate subject length
        if len(email_notification.subject) > 200:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has subject too long: "
                f"{len(email_notification.subject)} characters (max 200)"
            )
            return False

        # Validate email format
        if email_notification.email_format not in ["html", "text"]:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid email_format: "
                f"'{email_notification.email_format}'"
            )
            return False

        # Validate send status
        valid_statuses = ["pending", "sent", "failed", "bounced", "cancelled"]
        if email_notification.send_status not in valid_statuses:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid send_status: "
                f"'{email_notification.send_status}'"
            )
            return False

        # Validate priority
        if email_notification.priority not in ["low", "normal", "high"]:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has invalid priority: "
                f"'{email_notification.priority}'"
            )
            return False

        # Validate retry count
        if email_notification.retry_count < 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has negative retry_count: "
                f"{email_notification.retry_count}"
            )
            return False

        if email_notification.max_retries < 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has negative max_retries: "
                f"{email_notification.max_retries}"
            )
            return False

        # Validate click count
        if email_notification.click_count < 0:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has negative click_count: "
                f"{email_notification.click_count}"
            )
            return False

        # Validate attachment file size
        if (email_notification.attachment_file_size is not None and 
            email_notification.attachment_file_size < 0):
            self.logger.warning(
                f"Entity {email_notification.technical_id} has negative attachment_file_size: "
                f"{email_notification.attachment_file_size}"
            )
            return False

        return True

    def _validate_business_rules(self, email_notification: EmailNotification) -> bool:
        """
        Validate business rules and logical constraints.

        Args:
            email_notification: The EmailNotification entity to validate

        Returns:
            True if all business rules are satisfied, False otherwise
        """
        # Business rule: Retry count should not exceed max retries
        if email_notification.retry_count > email_notification.max_retries:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has retry_count ({email_notification.retry_count}) "
                f"exceeding max_retries ({email_notification.max_retries})"
            )
            return False

        # Business rule: If email is marked as sent, it should have actual_send_time
        if (email_notification.send_status == "sent" and 
            not email_notification.actual_send_time):
            self.logger.warning(
                f"Entity {email_notification.technical_id} is marked as sent but has no actual_send_time"
            )
            return False

        # Business rule: If email is opened, it should be sent first
        if (email_notification.email_opened and 
            email_notification.send_status not in ["sent"]):
            self.logger.warning(
                f"Entity {email_notification.technical_id} is marked as opened but not sent"
            )
            return False

        # Business rule: If there are attachment details, all should be present
        attachment_fields = [
            email_notification.attachment_file_path,
            email_notification.attachment_file_name,
            email_notification.attachment_file_size
        ]
        
        # Check if any attachment field is provided
        has_any_attachment = any(field is not None for field in attachment_fields)
        has_all_attachment = all(field is not None for field in attachment_fields)
        
        if has_any_attachment and not has_all_attachment:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has incomplete attachment information"
            )
            return False

        # Business rule: Recipient should be the expected sales team email
        expected_recipient = "victoria.sagdieva@cyoda.com"
        if email_notification.recipient_email != expected_recipient:
            self.logger.warning(
                f"Entity {email_notification.technical_id} has unexpected recipient: "
                f"'{email_notification.recipient_email}' (expected: '{expected_recipient}')"
            )
            # This is a warning, not a failure - might be valid for testing

        # Business rule: Email body should contain report-related content for performance reports
        if email_notification.report_id:
            report_keywords = ["performance", "report", "sales", "inventory", "analysis"]
            body_lower = email_notification.email_body.lower()
            
            if not any(keyword in body_lower for keyword in report_keywords):
                self.logger.warning(
                    f"Entity {email_notification.technical_id} has report_id but email body "
                    f"doesn't contain report-related keywords"
                )
                # This is a warning, not a failure

        return True

    def _is_valid_email(self, email: str) -> bool:
        """
        Check if an email address is valid using regex pattern.

        Args:
            email: The email address to validate

        Returns:
            True if email is valid, False otherwise
        """
        if not email or len(email.strip()) == 0:
            return False
        
        return bool(self.email_pattern.match(email.strip()))
