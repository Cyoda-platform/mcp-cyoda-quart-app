"""
Subscriber Processors for Cat Facts Subscription System

Handles subscriber confirmation, activation, and related business logic
for the subscription workflow.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SubscriberConfirmationProcessor(CyodaProcessor):
    """
    Processor for sending confirmation emails to new subscribers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberConfirmationProcessor",
            description="Sends confirmation email to new subscribers and updates subscription status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber confirmation by sending confirmation email.

        Args:
            entity: The Subscriber entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing subscriber confirmation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Simulate sending confirmation email
            await self._send_confirmation_email(subscriber)

            # Update subscriber status
            subscriber.subscription_status = "pending"
            subscriber.update_timestamp()

            self.logger.info(
                f"Confirmation email sent to subscriber {subscriber.technical_id}"
            )

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber confirmation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_confirmation_email(self, subscriber: Subscriber) -> None:
        """
        Send confirmation email to subscriber.

        Args:
            subscriber: The subscriber to send confirmation email to
        """
        # In a real implementation, this would integrate with an email service
        # For now, we'll just log the action
        self.logger.info(
            f"Sending confirmation email to {subscriber.email} for subscriber {subscriber.technical_id}"
        )

        # Simulate email sending delay
        import asyncio

        await asyncio.sleep(0.1)

        self.logger.info(f"Confirmation email sent successfully to {subscriber.email}")


class SubscriberActivationProcessor(CyodaProcessor):
    """
    Processor for activating confirmed subscribers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberActivationProcessor",
            description="Activates confirmed subscribers and sets up their subscription",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber activation.

        Args:
            entity: The Subscriber entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing subscriber activation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Activate the subscription
            subscriber.activate_subscription()

            # Send welcome email
            await self._send_welcome_email(subscriber)

            self.logger.info(
                f"Subscriber {subscriber.technical_id} activated successfully"
            )

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_welcome_email(self, subscriber: Subscriber) -> None:
        """
        Send welcome email to newly activated subscriber.

        Args:
            subscriber: The subscriber to send welcome email to
        """
        # In a real implementation, this would integrate with an email service
        self.logger.info(
            f"Sending welcome email to {subscriber.email} for subscriber {subscriber.technical_id}"
        )

        # Simulate email sending delay
        import asyncio

        await asyncio.sleep(0.1)

        self.logger.info(f"Welcome email sent successfully to {subscriber.email}")
