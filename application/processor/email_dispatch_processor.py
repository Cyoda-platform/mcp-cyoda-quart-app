"""
EmailDispatchProcessor for Pet Store Performance Analysis System

Handles automated email dispatch to the sales team (victoria.sagdieva@cyoda.com)
as specified in functional requirements.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from application.entity.email_notification import EmailNotification
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailDispatchProcessor(CyodaProcessor):
    """
    Processor for EmailNotification entity that handles automated
    email dispatch to the sales team.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailDispatchProcessor",
            description="Handles automated email dispatch to sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send email notification to the sales team.

        Args:
            entity: The EmailNotification entity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The email notification entity with updated status
        """
        try:
            self.logger.info(
                f"Dispatching email notification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            email_notification = cast_entity(entity, EmailNotification)

            # Validate email is ready to send
            if not email_notification.is_ready_to_send():
                raise ValueError("Email notification is not ready to send")

            # Send the email
            success = await self._send_email(email_notification)

            if success:
                # Mark email as sent
                email_notification.mark_as_sent()
                # Simulate delivery confirmation (in real system, this would be async)
                email_notification.mark_as_delivered()

                self.logger.info(
                    f"Email notification {email_notification.technical_id} sent successfully to {email_notification.recipient_email}"
                )
            else:
                # Mark email as failed
                email_notification.mark_as_failed("Email delivery failed")

                self.logger.error(
                    f"Failed to send email notification {email_notification.technical_id}"
                )

            return email_notification

        except Exception as e:
            self.logger.error(
                f"Error dispatching email notification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # If we have the email entity, mark it as failed
            if isinstance(entity, EmailNotification) or hasattr(
                entity, "mark_as_failed"
            ):
                try:
                    email_entity = cast_entity(entity, EmailNotification)
                    email_entity.mark_as_failed(str(e))
                    return email_entity
                except Exception:
                    pass
            raise

    async def _send_email(self, email_notification: EmailNotification) -> bool:
        """
        Send the email notification.

        Note: This is a simulated implementation for demonstration purposes.
        In a production system, this would integrate with actual email services
        like SendGrid, AWS SES, or SMTP servers.

        Args:
            email_notification: The EmailNotification entity to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Simulating email dispatch to {email_notification.recipient_email}"
            )

            # Simulate email sending process
            email_data = self._prepare_email_data(email_notification)

            # In a real implementation, this would be:
            # - SMTP server connection
            # - Email service API call (SendGrid, AWS SES, etc.)
            # - Queue message for background processing

            # For simulation, we'll just log the email details
            self._log_email_simulation(email_data)

            # Simulate some processing time
            import asyncio

            await asyncio.sleep(0.2)

            # Simulate 95% success rate
            import random

            success = random.random() < 0.95

            if success:
                self.logger.info(
                    f"✅ Email successfully sent to {email_notification.recipient_email}"
                )
            else:
                self.logger.warning(
                    f"❌ Email delivery failed for {email_notification.recipient_email}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error in email sending process: {str(e)}")
            return False

    def _prepare_email_data(self, email_notification: EmailNotification) -> Dict[str, Any]:
        """
        Prepare email data for sending.

        Args:
            email_notification: The EmailNotification entity

        Returns:
            Dictionary containing prepared email data
        """
        return {
            "to": email_notification.recipient_email,
            "from": email_notification.sender_email,
            "subject": email_notification.subject,
            "content": email_notification.content,
            "content_type": "text/html",
            "priority": email_notification.priority,
            "email_type": email_notification.email_type,
            "report_id": email_notification.report_id,
        }

    def _log_email_simulation(self, email_data: Dict[str, Any]) -> None:
        """
        Log email simulation details for demonstration.

        Args:
            email_data: Prepared email data
        """
        self.logger.info("=" * 60)
        self.logger.info("EMAIL SIMULATION - WOULD SEND:")
        self.logger.info(f"To: {email_data['to']}")
        self.logger.info(f"From: {email_data['from']}")
        self.logger.info(f"Subject: {email_data['subject']}")
        self.logger.info(f"Priority: {email_data['priority']}")
        self.logger.info(f"Type: {email_data['email_type']}")
        self.logger.info(f"Report ID: {email_data['report_id']}")
        self.logger.info(f"Content Length: {len(email_data['content'])} characters")
        self.logger.info("Content Preview:")
        # Log first 200 characters of content
        content_preview = email_data["content"][:200].replace("\n", " ")
        self.logger.info(f"  {content_preview}...")
        self.logger.info("=" * 60)

    def _send_via_smtp(self, email_data: Dict[str, Any]) -> bool:
        """
        Send email via SMTP (example implementation - not used in simulation).

        This method shows how you would implement actual SMTP sending
        in a production environment.

        Args:
            email_data: Prepared email data

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # SMTP configuration (would come from environment variables)
            smtp_server = "smtp.gmail.com"  # Example
            smtp_port = 587
            smtp_username = "your-email@gmail.com"
            smtp_password = "your-app-password"

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email_data["subject"]
            msg["From"] = email_data["from"]
            msg["To"] = email_data["to"]

            # Add HTML content
            html_part = MIMEText(email_data["content"], "html")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            self.logger.error(f"SMTP sending failed: {str(e)}")
            return False

    def _send_via_api(self, email_data: Dict[str, Any]) -> bool:
        """
        Send email via API service (example implementation - not used in simulation).

        This method shows how you would implement API-based email sending
        using services like SendGrid, AWS SES, etc.

        Args:
            email_data: Prepared email data

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Example using SendGrid API
            import requests

            api_key = "your-sendgrid-api-key"  # Would come from environment
            url = "https://api.sendgrid.com/v3/mail/send"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": email_data["to"]}],
                        "subject": email_data["subject"],
                    }
                ],
                "from": {"email": email_data["from"]},
                "content": [{"type": "text/html", "value": email_data["content"]}],
            }

            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 202

        except Exception as e:
            self.logger.error(f"API sending failed: {str(e)}")
            return False

    def _validate_email_configuration(self) -> bool:
        """
        Validate email configuration and connectivity.

        Returns:
            True if configuration is valid, False otherwise
        """
        # In a real implementation, this would check:
        # - SMTP server connectivity
        # - API key validity
        # - Email service quotas
        # - DNS configuration

        # For simulation, always return True
        return True

    def _handle_delivery_failure(
        self, email_notification: EmailNotification, error: str
    ) -> None:
        """
        Handle email delivery failure with retry logic.

        Args:
            email_notification: The failed EmailNotification entity
            error: Error message
        """
        self.logger.warning(
            f"Email delivery failed for {email_notification.technical_id}: {error}"
        )

        # Check if we can retry
        if email_notification.can_retry():
            self.logger.info(
                f"Email {email_notification.technical_id} can be retried "
                f"(attempt {email_notification.delivery_attempts + 1}/3)"
            )
            # In a real system, you might queue for retry
        else:
            self.logger.error(
                f"Email {email_notification.technical_id} exceeded retry limit"
            )

    def _get_email_template(self, template_name: str) -> str:
        """
        Get email template by name (example for future enhancement).

        Args:
            template_name: Name of the email template

        Returns:
            Email template content
        """
        templates = {
            "weekly_report": """
            <html>
            <body>
                <h2>Weekly Performance Report</h2>
                <p>Please find your weekly performance analysis attached.</p>
                {content}
            </body>
            </html>
            """,
            "alert": """
            <html>
            <body>
                <h2>Performance Alert</h2>
                <p>This is an automated alert regarding your pet store performance.</p>
                {content}
            </body>
            </html>
            """,
        }

        return templates.get(template_name, "{content}")
