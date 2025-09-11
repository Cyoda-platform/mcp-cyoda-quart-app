"""
MailSendGloomyMailProcessor for Cyoda Client Application

Processes and sends gloomy mail to the recipients in the mail list.
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


class MailSendGloomyMailProcessor(CyodaProcessor):
    """
    Processor for Mail entity that sends gloomy mail to recipients.
    Validates that the mail is gloomy and sends thoughtful content to all recipients.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailSendGloomyMailProcessor",
            description="Processes Mail entities and sends gloomy mail to recipients",
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
        Process the Mail entity and send gloomy mail to recipients.

        Args:
            entity: The Mail entity to process (must be in 'pending' state with isHappy=false)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity (state will be updated to 'gloomy_sent' by workflow)
        """
        try:
            self.logger.info(
                f"Processing Mail entity {getattr(entity, 'technical_id', '<unknown>')} for gloomy mail"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate that this is a gloomy mail
            if mail_entity.is_happy:
                raise ValueError(
                    "MailSendGloomyMailProcessor can only process gloomy mails (isHappy=false)"
                )

            # Validate that mail list is not empty
            if not mail_entity.mail_list:
                raise ValueError("Mail list cannot be empty")

            # Generate gloomy mail content
            subject = "☔ Reflective Mail - A Moment of Contemplation ☔"
            body = self._generate_gloomy_mail_content()

            # Send email to each recipient
            for email in mail_entity.mail_list:
                try:
                    await self._send_email(email, subject, body)
                    self.logger.info(f"Successfully sent gloomy mail to {email}")
                except Exception as e:
                    self.logger.error(
                        f"Failed to send gloomy mail to {email}: {str(e)}"
                    )
                    raise

            self.logger.info(
                f"Mail entity {mail_entity.technical_id} processed successfully - gloomy mail sent to {len(mail_entity.mail_list)} recipients"
            )

            return mail_entity

        except Exception as e:
            self.logger.error(
                f"Error processing Mail entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _generate_gloomy_mail_content(self) -> str:
        """Generate thoughtful mail content with introspective messages and gentle support"""
        return """
☔ Dear Friend,

Sometimes life feels heavy, and that's okay. We all have moments when the world seems a little gray.

In these quiet moments, remember:
• 🌙 It's natural to feel sad sometimes - emotions are part of being human
• 🍃 Even storms pass, and calm follows after
• 🕯️ Small acts of self-care can bring comfort
• 📖 Reflection can lead to deeper understanding
• 🤝 You don't have to face difficult times alone

Take your time to process what you're feeling. There's wisdom in sitting with our emotions, even the uncomfortable ones.

"The wound is the place where the Light enters you." - Rumi

Be gentle with yourself today. Tomorrow may bring new perspectives.

With understanding and support,
The Reflective Mail Team 🌿
        """.strip()

    async def _send_email(self, recipient: str, subject: str, body: str) -> None:
        """
        Send email to recipient (mock implementation for demonstration)

        In a real implementation, this would integrate with an email service
        like SendGrid, AWS SES, or SMTP server.
        """
        # Mock email sending - in real implementation, integrate with email service
        self.logger.info(f"📧 Sending gloomy mail to {recipient}")
        self.logger.info(f"Subject: {subject}")
        self.logger.debug(f"Body: {body}")

        # Simulate email sending delay and potential failure
        import asyncio

        await asyncio.sleep(0.1)  # Simulate network delay

        # In real implementation, this would be actual email sending logic
        # Example with SendGrid or similar:
        # await email_service.send(to=recipient, subject=subject, body=body)
