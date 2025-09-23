"""
EmailNotification Processors for Cyoda Client Application

Handles all EmailNotification entity workflow transitions and business logic processing.
Implements processors for notification creation, email sending, delivery confirmation, failure handling, and retry logic.
"""

import logging
from typing import Any

from application.entity.emailnotification.version_1.email_notification import (
    EmailNotification,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreateNotificationProcessor(CyodaProcessor):
    """
    Processor for creating email notifications.
    Initializes email notification with content and recipient information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateNotificationProcessor",
            description="Creates email notification with content and recipient information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email notification creation according to functional requirements.

        Args:
            entity: The EmailNotification entity to create
            **kwargs: Additional processing parameters

        Returns:
            The created email notification entity
        """
        try:
            self.logger.info(
                f"Creating email notification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Set default values if not provided
            if not notification.delivery_status:
                notification.delivery_status = "pending"

            if notification.retry_count is None:
                notification.retry_count = 0

            # Update timestamp
            notification.update_timestamp()

            self.logger.info(
                f"Email notification {notification.technical_id} created successfully for {notification.recipient_email}"
            )

            return notification

        except Exception as e:
            self.logger.error(
                f"Error creating email notification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class SendEmailProcessor(CyodaProcessor):
    """
    Processor for sending email notifications.
    Handles SMTP email delivery with error handling.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SendEmailProcessor",
            description="Sends email notifications via SMTP with error handling",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email sending according to functional requirements.

        Args:
            entity: The EmailNotification entity to send
            **kwargs: Additional processing parameters

        Returns:
            The email notification entity with updated status
        """
        try:
            self.logger.info(
                f"Sending email notification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Update status to sending
            notification.delivery_status = "sending"
            notification.update_timestamp()

            # Attempt to send email
            success = await self._send_email_via_smtp(notification)

            if success:
                # Mark as sent
                notification.mark_as_sent()
                self.logger.info(
                    f"Email notification {notification.technical_id} sent successfully to {notification.recipient_email}"
                )
            else:
                # Mark as failed and increment retry count
                notification.mark_as_failed()
                notification.increment_retry_count()
                self.logger.warning(
                    f"Email notification {notification.technical_id} failed to send (attempt {notification.retry_count})"
                )

            return notification

        except Exception as e:
            self.logger.error(
                f"Error sending email notification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark as failed on exception
            notification = cast_entity(entity, EmailNotification)
            notification.mark_as_failed()
            notification.increment_retry_count()
            return notification

    async def _send_email_via_smtp(self, notification: EmailNotification) -> bool:
        """
        Send email via SMTP service.

        Args:
            notification: The email notification to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # TODO: Implement actual SMTP email sending
            # For now, simulate email sending
            self.logger.info(
                f"Sending email to {notification.recipient_email} with subject: {notification.subject}"
            )

            # Simulate email sending success/failure
            # In real implementation, this would use SMTP library
            return True  # Simulate success

        except Exception as e:
            self.logger.error(f"SMTP sending failed: {str(e)}")
            return False


class ConfirmDeliveryProcessor(CyodaProcessor):
    """
    Processor for confirming email delivery.
    Marks email as successfully delivered.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ConfirmDeliveryProcessor",
            description="Confirms successful email delivery",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process delivery confirmation according to functional requirements.

        Args:
            entity: The EmailNotification entity to confirm
            **kwargs: Additional processing parameters

        Returns:
            The confirmed email notification entity
        """
        try:
            self.logger.info(
                f"Confirming delivery for email notification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Mark as sent if not already
            if notification.delivery_status != "sent":
                notification.mark_as_sent()

            self.logger.info(
                f"Email notification {notification.technical_id} delivery confirmed"
            )

            return notification

        except Exception as e:
            self.logger.error(
                f"Error confirming delivery for email notification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class MarkFailedProcessor(CyodaProcessor):
    """
    Processor for marking email notifications as failed.
    Handles permanent failure after maximum retry attempts.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MarkFailedProcessor",
            description="Marks email notification as permanently failed after max retries",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process failure marking according to functional requirements.

        Args:
            entity: The EmailNotification entity to mark as failed
            **kwargs: Additional processing parameters

        Returns:
            The failed email notification entity
        """
        try:
            self.logger.info(
                f"Marking email notification as failed {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Mark as failed
            notification.mark_as_failed()

            # Check if max retries reached
            if notification.retry_count >= notification.MAX_RETRY_ATTEMPTS:
                self.logger.warning(
                    f"Email notification {notification.technical_id} permanently failed after {notification.retry_count} attempts"
                )
            else:
                self.logger.info(
                    f"Email notification {notification.technical_id} marked as failed (attempt {notification.retry_count})"
                )

            return notification

        except Exception as e:
            self.logger.error(
                f"Error marking email notification as failed {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class RetrySendProcessor(CyodaProcessor):
    """
    Processor for retrying failed email notifications.
    Attempts to resend failed emails within retry limits.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RetrySendProcessor",
            description="Retries sending failed email notifications within retry limits",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email retry according to functional requirements.

        Args:
            entity: The EmailNotification entity to retry
            **kwargs: Additional processing parameters

        Returns:
            The retried email notification entity
        """
        try:
            self.logger.info(
                f"Retrying email notification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Check if retry is allowed
            if not notification.can_retry():
                self.logger.warning(
                    f"Email notification {notification.technical_id} cannot be retried "
                    f"(retry_count: {notification.retry_count}, max: {notification.MAX_RETRY_ATTEMPTS})"
                )
                return notification

            # Update status to sending for retry
            notification.delivery_status = "sending"
            notification.update_timestamp()

            # Attempt to send email again
            success = await self._send_email_via_smtp(notification)

            if success:
                # Mark as sent
                notification.mark_as_sent()
                self.logger.info(
                    f"Email notification {notification.technical_id} retry successful"
                )
            else:
                # Mark as failed and increment retry count
                notification.mark_as_failed()
                notification.increment_retry_count()
                self.logger.warning(
                    f"Email notification {notification.technical_id} retry failed (attempt {notification.retry_count})"
                )

            return notification

        except Exception as e:
            self.logger.error(
                f"Error retrying email notification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark as failed on exception
            notification = cast_entity(entity, EmailNotification)
            notification.mark_as_failed()
            notification.increment_retry_count()
            return notification

    async def _send_email_via_smtp(self, notification: EmailNotification) -> bool:
        """
        Send email via SMTP service (same as SendEmailProcessor).

        Args:
            notification: The email notification to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # TODO: Implement actual SMTP email sending
            # For now, simulate email sending
            self.logger.info(
                f"Retrying email to {notification.recipient_email} with subject: {notification.subject}"
            )

            # Simulate email sending success/failure
            # In real implementation, this would use SMTP library
            return True  # Simulate success

        except Exception as e:
            self.logger.error(f"SMTP retry sending failed: {str(e)}")
            return False
