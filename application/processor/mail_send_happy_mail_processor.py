"""
MailSendHappyMailProcessor for Cyoda Client Application

Processes and sends happy mail messages to the recipients in the mail list.
"""

import re
from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class MailSendHappyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that sends happy mail messages.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendHappyMailProcessor",
            description="Processes and sends happy mail messages to recipients",
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Mail entity and send happy mail messages.

        Args:
            entity: The Mail entity to process (must have isHappy=true)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity

        Raises:
            Exception: If processing fails
        """
        try:
            self.logger.info(
                f"Processing Mail entity {getattr(entity, 'technical_id', '<unknown>')} for happy mail sending"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate mail list is not empty
            if not mail_entity.mail_list or len(mail_entity.mail_list) == 0:
                raise ValueError("Mail list cannot be empty")

            # Validate all email addresses in mail list are valid format
            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            for email in mail_entity.mail_list:
                if not email_pattern.match(email.strip()):
                    raise ValueError(f"Invalid email address format: {email}")

            # Generate happy mail content
            subject = "🌟 Happy Mail - Brighten Your Day!"
            body = self._create_happy_mail_content()

            # Send email to each recipient
            successful_deliveries = 0
            failed_deliveries = 0

            for email in mail_entity.mail_list:
                try:
                    # Simulate sending email (in real implementation, use actual email service)
                    await self._send_email(email.strip(), subject, body)
                    self.logger.info(f"Successfully sent happy mail to {email}")
                    successful_deliveries += 1
                except Exception as e:
                    self.logger.error(f"Failed to send happy mail to {email}: {str(e)}")
                    failed_deliveries += 1
                    # Continue with remaining emails

            # If all emails failed, throw exception to trigger FAILED state
            if successful_deliveries == 0 and failed_deliveries > 0:
                raise Exception(
                    f"Failed to send happy mail to all {failed_deliveries} recipients"
                )

            self.logger.info(
                f"Happy mail processing completed for Mail {mail_entity.technical_id}. "
                f"Successful: {successful_deliveries}, Failed: {failed_deliveries}"
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing Mail entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_happy_mail_content(self) -> str:
        """
        Create cheerful, positive message content for happy mail.

        Returns:
            Happy mail body content
        """
        return """
🌟 Hello there! 🌟

We hope this message finds you in great spirits! We wanted to take a moment to brighten your day with some positive vibes.

✨ Remember that every day is a new opportunity to shine
🌈 Your smile can light up someone else's world
🎉 You are capable of amazing things
💫 The best is yet to come!

Keep spreading joy and positivity wherever you go. You make the world a better place just by being you!

Have a wonderful and happy day! 🌞

With warm regards and happy thoughts,
The Happy Mail Team 💝
        """.strip()

    async def _send_email(self, recipient: str, subject: str, body: str) -> None:
        """
        Send email to recipient (simulated implementation).

        Args:
            recipient: Email address of the recipient
            subject: Email subject
            body: Email body content

        Raises:
            Exception: If email sending fails
        """
        # In a real implementation, this would use an actual email service
        # For now, we'll simulate the email sending process
        self.logger.info(f"Sending email to {recipient} with subject: {subject}")

        # Simulate potential email sending failure (5% chance)
        import random

        if random.random() < 0.05:  # nosec B311
            raise Exception(f"Simulated email delivery failure for {recipient}")

        # Simulate email sending delay
        import asyncio

        await asyncio.sleep(0.1)

        self.logger.debug(f"Email successfully sent to {recipient}")
