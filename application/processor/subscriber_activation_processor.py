"""
SubscriberActivationProcessor for Cyoda Client Application

Activates subscriber after email verification.
Updates subscriber state and sends confirmation email.
"""

import logging
from typing import Any, Optional, cast

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SubscriberActivationProcessor(CyodaProcessor):
    """
    Processor for subscriber activation that handles email verification
    and activates the subscription.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberActivationProcessor",
            description="Activates subscriber after email verification",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber activation according to functional requirements.

        Args:
            entity: The Subscriber entity to activate (must be in pending state)
            **kwargs: Additional processing parameters

        Returns:
            The activated subscriber entity
        """
        try:
            self.logger.info(
                f"Processing subscriber activation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Validate subscriber exists and is in pending state
            if subscriber.state != "pending":
                raise ValueError(
                    f"Subscriber must be in pending state, current state: {subscriber.state}"
                )

            # Activate the subscription
            subscriber.activate_subscription()

            # Send confirmation email (simulated)
            await self._send_confirmation_email(subscriber)

            # Log activation event
            self.logger.info(f"Subscriber {subscriber.email} activated successfully")

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_confirmation_email(self, subscriber: Subscriber) -> None:
        """
        Send confirmation email to activated subscriber (simulated).

        Args:
            subscriber: The activated subscriber
        """
        try:
            # In a real implementation, this would send an actual email
            # For now, we just log the action
            self.logger.info(f"Sending confirmation email to {subscriber.email}")

            # Simulate email sending
            self.logger.info(
                f"Confirmation email sent successfully to {subscriber.email}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send confirmation email to {subscriber.email}: {str(e)}"
            )
            # Don't fail the activation if email sending fails
            pass
