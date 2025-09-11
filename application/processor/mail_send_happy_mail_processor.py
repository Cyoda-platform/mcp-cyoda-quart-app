"""
MailSendHappyMailProcessor for Cyoda Client Application

Processes and sends happy mail to the recipients in the mail list.
"""

import logging
from typing import Any, Optional, Protocol, cast, runtime_checkable

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def save(
        self, *, entity: dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class MailSendHappyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that sends happy mail to recipients.
    Validates that the mail is happy and sends cheerful content to all recipients.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendHappyMailProcessor",
            description="Processes Mail entities and sends happy mail to recipients",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Mail entity and send happy mail to recipients.

        Args:
            entity: The Mail entity to process (must be in 'pending' state with isHappy=true)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity (state will be updated to 'happy_sent' by workflow)
        """
        try:
            self.logger.info(
                f"Processing Mail entity {getattr(entity, 'technical_id', '<unknown>')} for happy mail"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate that this is a happy mail
            if not mail_entity.is_happy:
                raise ValueError(
                    "MailSendHappyMailProcessor can only process happy mails (isHappy=true)"
                )

            # Validate that mail list is not empty
            if not mail_entity.mail_list:
                raise ValueError("Mail list cannot be empty")

            # Generate happy mail content
            subject = "🌟 Happy Mail - Brighten Your Day! 🌟"
            body = self._generate_happy_mail_content()

            # Send email to each recipient
            for email in mail_entity.mail_list:
                try:
                    await self._send_email(email, subject, body)
                    self.logger.info(f"Successfully sent happy mail to {email}")
                except Exception as e:
                    self.logger.error(f"Failed to send happy mail to {email}: {str(e)}")
                    raise

            self.logger.info(
                f"Mail entity {mail_entity.technical_id} processed successfully - happy mail sent to {len(mail_entity.mail_list)} recipients"
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing Mail entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _generate_happy_mail_content(self) -> str:
        """Generate cheerful mail content with positive messages and emojis"""
        return """
🌟 Hello there! 🌟

We hope this message finds you having a wonderful day! ✨

Here are some positive thoughts to brighten your day:
• 🌈 Every day is a new opportunity to shine
• 🌻 Your smile can light up someone's world
• 🎉 Celebrate the small victories in life
• 💫 You are capable of amazing things
• 🌸 Spread kindness wherever you go

Remember: "The best way to cheer yourself up is to try to cheer somebody else up." - Mark Twain

Have a fantastic day ahead! 🌞

With warm wishes and positive vibes,
The Happy Mail Team 💝
        """.strip()

    async def _send_email(self, recipient: str, subject: str, body: str) -> None:
        """
        Send email to recipient (mock implementation for demonstration)

        In a real implementation, this would integrate with an email service
        like SendGrid, AWS SES, or SMTP server.
        """
        # Mock email sending - in real implementation, integrate with email service
        self.logger.info(f"📧 Sending happy mail to {recipient}")
        self.logger.info(f"Subject: {subject}")
        self.logger.debug(f"Body: {body}")

        # Simulate email sending delay and potential failure
        import asyncio

        await asyncio.sleep(0.1)  # Simulate network delay

        # In real implementation, this would be actual email sending logic
        # Example with SendGrid or similar:
        # await email_service.send(to=recipient, subject=subject, body=body)
