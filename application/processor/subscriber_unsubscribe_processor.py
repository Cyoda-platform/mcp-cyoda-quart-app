"""
SubscriberUnsubscribeProcessor for Cyoda Client Application

Processes unsubscription request and deactivates subscriber.
Handles both direct unsubscribe and token-based unsubscribe.
"""

import logging
from typing import Any, Optional, cast

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SubscriberUnsubscribeProcessor(CyodaProcessor):
    """
    Processor for subscriber unsubscription that handles deactivation
    and sends unsubscribe confirmation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberUnsubscribeProcessor",
            description="Processes unsubscription request",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber unsubscription according to functional requirements.

        Args:
            entity: The Subscriber entity to unsubscribe
            **kwargs: Additional processing parameters (may include unsubscribe_token)

        Returns:
            The unsubscribed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing subscriber unsubscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Validate subscriber exists
            if not subscriber.email:
                raise ValueError("Subscriber email is required")

            # Check if unsubscribe token is provided and matches
            unsubscribe_token = kwargs.get("unsubscribe_token")
            if unsubscribe_token and unsubscribe_token != subscriber.unsubscribe_token:
                raise ValueError("Invalid unsubscribe token")

            # Deactivate the subscription
            subscriber.deactivate_subscription()

            # Send unsubscribe confirmation email (simulated)
            await self._send_unsubscribe_confirmation_email(subscriber)

            # Log unsubscribe event
            self.logger.info(f"Subscriber {subscriber.email} unsubscribed successfully")

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber unsubscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_unsubscribe_confirmation_email(
        self, subscriber: Subscriber
    ) -> None:
        """
        Send unsubscribe confirmation email (simulated).

        Args:
            subscriber: The unsubscribed subscriber
        """
        try:
            # In a real implementation, this would send an actual email
            # For now, we just log the action
            self.logger.info(
                f"Sending unsubscribe confirmation email to {subscriber.email}"
            )

            # Simulate email sending
            self.logger.info(
                f"Unsubscribe confirmation email sent successfully to {subscriber.email}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send unsubscribe confirmation email to {subscriber.email}: {str(e)}"
            )
            # Don't fail the unsubscription if email sending fails
            pass
