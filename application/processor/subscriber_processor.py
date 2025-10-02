"""
Subscriber Processors for Cat Fact Subscription Application

Handles subscriber registration, unsubscription, and resubscription logic.
"""

import logging
from typing import Any

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SubscriberRegistrationProcessor(CyodaProcessor):
    """
    Processor for handling new subscriber registration.
    Sets up initial subscriber data and preferences.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberRegistrationProcessor",
            description="Processes new subscriber registration and sets up initial preferences",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber registration.

        Args:
            entity: The Subscriber entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing subscriber registration for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Ensure email is normalized
            if subscriber.email:
                subscriber.email = subscriber.email.lower().strip()

            # Set default subscription source if not provided
            if not subscriber.subscription_source:
                subscriber.subscription_source = "web"

            # Ensure subscriber is active
            subscriber.is_active = True

            self.logger.info(
                f"Subscriber {subscriber.email} registered successfully with ID {subscriber.technical_id}"
            )

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class SubscriberUnsubscribeProcessor(CyodaProcessor):
    """
    Processor for handling subscriber unsubscription.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberUnsubscribeProcessor",
            description="Processes subscriber unsubscription requests",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber unsubscription.

        Args:
            entity: The Subscriber entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing unsubscription for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Mark as unsubscribed
            subscriber.unsubscribe()

            self.logger.info(f"Subscriber {subscriber.email} unsubscribed successfully")

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing unsubscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class SubscriberResubscribeProcessor(CyodaProcessor):
    """
    Processor for handling subscriber resubscription.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberResubscribeProcessor",
            description="Processes subscriber resubscription requests",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscriber resubscription.

        Args:
            entity: The Subscriber entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity
        """
        try:
            self.logger.info(
                f"Processing resubscription for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Reactivate subscription
            subscriber.resubscribe()

            self.logger.info(f"Subscriber {subscriber.email} resubscribed successfully")

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing resubscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
