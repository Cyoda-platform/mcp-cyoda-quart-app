"""
MailSendGloomyMailProcessor for Cyoda Client Application

Processes and sends gloomy mail messages to the recipients in the mail list.
"""

import re
from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class MailSendGloomyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that sends gloomy mail messages.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendGloomyMailProcessor",
            description="Processes and sends gloomy mail messages to recipients",
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Mail entity and send gloomy mail messages.

        Args:
            entity: The Mail entity to process (must have isHappy=false)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity

        Raises:
            Exception: If processing fails
        """
        try:
            self.logger.info(
                f"Processing Mail entity {getattr(entity, 'technical_id', '<unknown>')} for gloomy mail sending"
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

            # Generate gloomy mail content
            subject = "☔ Gloomy Mail - Sharing the Blues"
            body = self._create_gloomy_mail_content()

            # Send email to each recipient
            successful_deliveries = 0
            failed_deliveries = 0

            for email in mail_entity.mail_list:
                try:
                    # Simulate sending email (in real implementation, use actual email service)
                    await self._send_email(email.strip(), subject, body)
                    self.logger.info(f"Successfully sent gloomy mail to {email}")
                    successful_deliveries += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to send gloomy mail to {email}: {str(e)}"
                    )
                    failed_deliveries += 1
                    # Continue with remaining emails

            # If all emails failed, throw exception to trigger FAILED state
            if successful_deliveries == 0 and failed_deliveries > 0:
                raise Exception(
                    f"Failed to send gloomy mail to all {failed_deliveries} recipients"
                )

            self.logger.info(
                f"Gloomy mail processing completed for Mail {mail_entity.technical_id}. "
                f"Successful: {successful_deliveries}, Failed: {failed_deliveries}"
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing Mail entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_gloomy_mail_content(self) -> str:
        """
        Create melancholic, somber message content for gloomy mail.

        Returns:
            Gloomy mail body content
        """
        return """
☔ Greetings in these gray times ☔

Sometimes the world feels heavy, and the skies seem perpetually overcast. We understand that not every day can be filled with sunshine and rainbows.

🌧️ It's okay to feel melancholic sometimes
🌫️ Gray days remind us to appreciate the bright ones
💭 Reflection and introspection have their own value
🍂 Even in sadness, there can be beauty and meaning

Life isn't always cheerful, and that's perfectly human. These quieter, more somber moments are part of our shared experience.

Take your time to feel what you need to feel. Tomorrow may bring different weather, both outside and within.

In solidarity with the blues,
The Gloomy Mail Team 🌙
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
