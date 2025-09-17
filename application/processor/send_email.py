"""
SendEmailProcessor for Cyoda Client Application

Sends email reports to subscribers with generated report content.
Updates delivery status according to workflow requirements.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SendEmailProcessor(CyodaProcessor):
    """
    Processor for Report that sends emails to subscribers.
    Simulates email sending and updates delivery status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="send_email",
            description="Sends email reports to subscribers",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send email report to all subscribers.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated delivery status
        """
        try:
            self.logger.info(
                f"Starting email sending for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate report content exists
            if not report.report_content:
                raise ValueError("Report content is required for email sending")

            # Send emails to all subscribers
            success = await self._send_emails_to_subscribers(report)

            # Update delivery status based on success
            if success:
                report.set_email_sent()
                self.logger.info(
                    f"Report {report.technical_id} sent successfully to {len(report.subscribers)} subscribers"
                )
            else:
                report.set_email_failed()
                self.logger.error(
                    f"Failed to send Report {report.technical_id} to subscribers"
                )

            return report

        except Exception as e:
            self.logger.error(
                f"Error sending email for Report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Set failed status on error
            if hasattr(entity, "set_email_failed"):
                entity.set_email_failed()
            raise

    async def _send_emails_to_subscribers(self, report: Report) -> bool:
        """
        Send emails to all subscribers.

        Note: This is a simulation for demo purposes.
        In a real implementation, this would integrate with an email service.
        """
        try:
            # Simulate email sending process
            self.logger.info(
                f"Simulating email sending to {len(report.subscribers)} subscribers"
            )

            for email in report.subscribers:
                # Validate email format (basic check)
                if "@" not in email or "." not in email:
                    self.logger.warning(f"Invalid email format: {email}")
                    continue

                # Simulate sending email
                content = report.report_content or ""
                await self._simulate_send_email(email, content)
                self.logger.info(f"Email sent to: {email}")

            self.logger.info("All emails sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error sending emails: {str(e)}")
            return False

    async def _simulate_send_email(self, email: str, content: str) -> None:
        """
        Simulate sending an email.

        In a real implementation, this would:
        1. Connect to SMTP server or email service API
        2. Format the email with proper headers
        3. Send the email
        4. Handle delivery confirmations
        """
        # Simulate email composition
        subject = "London Houses Data Analysis Report"

        # Log the simulated email (in production, this would be actual sending)
        self.logger.info(
            f"SIMULATED EMAIL SEND:\n"
            f"To: {email}\n"
            f"Subject: {subject}\n"
            f"Content Length: {len(content)} characters\n"
            f"Content Preview: {content[:100]}..."
        )

        # Simulate potential email sending delay
        import asyncio

        await asyncio.sleep(0.1)  # Small delay to simulate network operation
