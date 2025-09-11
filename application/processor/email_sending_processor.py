"""
EmailSendingProcessor for Cyoda Client Application

Sends email to subscriber with cat fact content.
Simulates email sending and updates delivery status.
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Any]: ...


class EmailSendingProcessor(CyodaProcessor):
    """
    Processor for sending emails to subscribers with cat fact content.
    Simulates email sending and updates delivery tracking.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailSendingProcessor",
            description="Sends email to subscriber with cat fact content",
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
        Process email sending according to functional requirements.

        Args:
            entity: The EmailDelivery entity to process (must be in pending state)
            **kwargs: Additional processing parameters

        Returns:
            The EmailDelivery entity with updated status
        """
        try:
            self.logger.info(
                f"Processing email sending {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailDelivery for type-safe operations
            email_delivery = cast_entity(entity, EmailDelivery)

            # Validate email delivery is in pending state
            if email_delivery.state != "pending":
                raise ValueError(
                    f"Email delivery must be in pending state, current state: {email_delivery.state}"
                )

            # Get subscriber and cat fact data
            subscriber_data = await self._get_subscriber_data(
                email_delivery.subscriber_id
            )
            cat_fact_data = await self._get_cat_fact_data(email_delivery.cat_fact_id)

            # Compose and send email
            await self._send_email(subscriber_data, cat_fact_data, email_delivery)

            # Mark as sent
            email_delivery.mark_sent()

            self.logger.info(
                f"Email sent successfully to {subscriber_data.get('email', 'unknown')} for delivery {email_delivery.get_id()}"
            )

            return email_delivery

        except Exception as e:
            self.logger.error(
                f"Error processing email sending {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark as failed and re-raise for failure processor
            email_delivery = cast_entity(entity, EmailDelivery)
            email_delivery.mark_failed(str(e))
            raise

    async def _get_subscriber_data(self, subscriber_id: str) -> dict[str, Any]:
        """Get subscriber data for email composition"""
        entity_service = self._get_entity_service()

        subscriber = await entity_service.get_by_id(
            entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
        )

        if not subscriber:
            raise ValueError(f"Subscriber {subscriber_id} not found")

        return subscriber.data if hasattr(subscriber, "data") else {}

    async def _get_cat_fact_data(self, cat_fact_id: str) -> dict[str, Any]:
        """Get cat fact data for email composition"""
        entity_service = self._get_entity_service()

        cat_fact = await entity_service.get_by_id(
            entity_id=cat_fact_id, entity_class="CatFact", entity_version="1"
        )

        if not cat_fact:
            raise ValueError(f"Cat fact {cat_fact_id} not found")

        return cat_fact.data if hasattr(cat_fact, "data") else {}

    async def _send_email(
        self,
        subscriber_data: dict[str, Any],
        cat_fact_data: dict[str, Any],
        email_delivery: EmailDelivery,
    ) -> None:
        """
        Send email with cat fact content (simulated).

        Args:
            subscriber_data: Subscriber information
            cat_fact_data: Cat fact content
            email_delivery: Email delivery record
        """
        try:
            email = subscriber_data.get("email", "unknown@example.com")
            fact_text = cat_fact_data.get("factText", "No fact available")
            unsubscribe_token = subscriber_data.get("unsubscribeToken", "")

            # Compose email content
            subject = "Your Weekly Cat Fact"
            body = self._compose_email_body(fact_text, unsubscribe_token)

            # Simulate email sending
            self.logger.info(f"Sending email to {email} with subject: {subject}")
            self.logger.debug(f"Email body preview: {body[:100]}...")

            # In a real implementation, this would use an email service
            # For now, we simulate successful sending

            self.logger.info(f"Email sent successfully to {email}")

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise

    def _compose_email_body(self, fact_text: str, unsubscribe_token: str) -> str:
        """Compose HTML email body with cat fact and unsubscribe link"""
        return f"""
        <html>
        <body>
            <h2>Your Weekly Cat Fact</h2>
            <p>{fact_text}</p>
            <hr>
            <p><small>
                Don't want to receive these emails? 
                <a href="https://example.com/unsubscribe?token={unsubscribe_token}">Unsubscribe here</a>
            </small></p>
        </body>
        </html>
        """
