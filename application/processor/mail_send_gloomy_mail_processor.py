"""
MailSendGloomyMailProcessor for Cyoda Client Application

Processes the sending of gloomy mail messages to the recipients in the mail list.
"""

import re
from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class MailSendGloomyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that handles sending gloomy mail messages.

    Validates mail list, generates gloomy content, and simulates sending emails
    to all recipients in the mail list.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendGloomyMailProcessor",
            description="Processes the sending of gloomy mail messages to recipients",
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Mail entity to send gloomy mail messages.

        Args:
            entity: The Mail entity to process (must have isHappy = false)

        Returns:
            The processed entity with updated metadata about send status
        """
        try:
            self.logger.info(
                f"Processing gloomy mail for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate that this is indeed a gloomy mail
            if mail_entity.isHappy:
                raise ValueError(
                    "MailSendGloomyMailProcessor can only process gloomy mails (isHappy=false)"
                )

            # Validate mailList is not empty
            if not mail_entity.mailList:
                raise ValueError("mailList cannot be empty")

            # Validate all email addresses in mailList are valid format
            self._validate_email_addresses(mail_entity.mailList)

            # Generate gloomy mail content
            subject = "☔ Gloomy Mail - Reflective Thoughts"
            body = self._generate_gloomy_mail_content()

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
                    self.logger.info(f"Gloomy mail sent successfully to {email}")
                except Exception as e:
                    send_results.append(
                        {
                            "email": email,
                            "status": "failed",
                            "error": str(e),
                            "timestamp": self._get_current_timestamp(),
                        }
                    )
                    self.logger.error(
                        f"Failed to send gloomy mail to {email}: {str(e)}"
                    )

            # Update mail entity with send results
            mail_entity.add_metadata("send_results", send_results)
            mail_entity.add_metadata("mail_type", "gloomy")
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
                f"Gloomy mail processing completed for entity {mail_entity.technical_id}. "
                f"Sent to {mail_entity.get_metadata('successful_sends')} recipients."
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing gloomy mail for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_email_addresses(self, email_list: list[str]) -> None:
        """Validate that all email addresses in the list are valid format"""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in email_list:
            if not email_pattern.match(email.strip()):
                raise ValueError(f"Invalid email address format: {email}")

    def _generate_gloomy_mail_content(self) -> str:
        """Generate thoughtful, melancholic message content for gloomy mail"""
        return """
☔ Greetings in this moment of reflection ☔

Sometimes the world feels heavy, and that's okay.

🌧️ In these quieter moments, we find space to think:
• It's natural to feel overwhelmed sometimes
• Sadness and melancholy are part of the human experience
• Even in darkness, there are lessons to be learned
• Tomorrow may bring different feelings

🌫️ Remember: It's okay to not be okay. Your feelings are valid. 🌫️

Take time to process, to feel, and to be gentle with yourself.
Sometimes we need the rain to appreciate the sunshine.

In solidarity and understanding,
The Reflective Mail Team 🕯️
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
