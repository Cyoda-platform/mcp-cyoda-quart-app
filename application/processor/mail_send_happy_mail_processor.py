"""
MailSendHappyMailProcessor for Cyoda Client Application

Processes the sending of happy mail messages to the recipients in the mail list.
"""

import re
from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class MailSendHappyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that handles sending happy mail messages.

    Validates mail list, generates happy content, and simulates sending emails
    to all recipients in the mail list.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendHappyMailProcessor",
            description="Processes the sending of happy mail messages to recipients",
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Mail entity to send happy mail messages.

        Args:
            entity: The Mail entity to process (must have isHappy = true)

        Returns:
            The processed entity with updated metadata about send status
        """
        try:
            self.logger.info(
                f"Processing happy mail for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate that this is indeed a happy mail
            if not mail_entity.isHappy:
                raise ValueError(
                    "MailSendHappyMailProcessor can only process happy mails (isHappy=true)"
                )

            # Validate mailList is not empty
            if not mail_entity.mailList:
                raise ValueError("mailList cannot be empty")

            # Validate all email addresses in mailList are valid format
            self._validate_email_addresses(mail_entity.mailList)

            # Generate happy mail content
            subject = "🌟 Happy Mail - Brighten Your Day!"
            body = self._generate_happy_mail_content()

            # Simulate sending email to each recipient
            send_results = []
            for email in mail_entity.mailList:
                try:
                    # Simulate email sending (in real implementation, this would use an email service)
                    self._simulate_send_email(email, subject, body)
                    send_results.append(
                        {
                            "email": email,
                            "status": "sent",
                            "timestamp": self._get_current_timestamp(),
                        }
                    )
                    self.logger.info(f"Happy mail sent successfully to {email}")
                except Exception as e:
                    send_results.append(
                        {
                            "email": email,
                            "status": "failed",
                            "error": str(e),
                            "timestamp": self._get_current_timestamp(),
                        }
                    )
                    self.logger.error(f"Failed to send happy mail to {email}: {str(e)}")

            # Update mail entity with send results
            mail_entity.add_metadata("send_results", send_results)
            mail_entity.add_metadata("mail_type", "happy")
            mail_entity.add_metadata("subject", subject)
            mail_entity.add_metadata("total_recipients", len(mail_entity.mailList))
            mail_entity.add_metadata(
                "successful_sends",
                len([r for r in send_results if r["status"] == "sent"]),
            )
            mail_entity.add_metadata(
                "failed_sends",
                len([r for r in send_results if r["status"] == "failed"]),
            )

            self.logger.info(
                f"Happy mail processing completed for entity {mail_entity.technical_id}. "
                f"Sent to {mail_entity.get_metadata('successful_sends')} recipients."
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing happy mail for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_email_addresses(self, email_list: list[str]) -> None:
        """Validate that all email addresses in the list are valid format"""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in email_list:
            if not email_pattern.match(email.strip()):
                raise ValueError(f"Invalid email address format: {email}")

    def _generate_happy_mail_content(self) -> str:
        """Generate cheerful, positive message content for happy mail"""
        return """
🌟 Hello there! 🌟

We hope this message finds you in great spirits!

✨ Here are some wonderful thoughts to brighten your day:
• Every day is a new opportunity to create something amazing
• Your smile can light up someone else's world
• Small acts of kindness create ripples of joy
• You are capable of incredible things

🌈 Remember: Life is beautiful, and so are you! 🌈

Wishing you sunshine, laughter, and endless happiness!

With warm regards and positive vibes,
The Happy Mail Team 💫
        """.strip()

    def _simulate_send_email(self, email: str, subject: str, body: str) -> None:
        """Simulate sending an email (placeholder for actual email service integration)"""
        # In a real implementation, this would integrate with an email service like:
        # - SendGrid
        # - AWS SES
        # - SMTP server
        # For now, we just log the action
        self.logger.debug(f"Simulating email send to {email} with subject: {subject}")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
