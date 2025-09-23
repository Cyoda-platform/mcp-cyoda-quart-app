"""
WeatherSubscription Processors for Cyoda Client Application

Handles all WeatherSubscription entity workflow transitions and business logic processing.
Implements processors for subscription creation, activation, pausing, resuming, and cancellation.
"""

import logging
from typing import Any

from application.entity.weathersubscription.version_1.weather_subscription import (
    WeatherSubscription,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CreateSubscriptionProcessor(CyodaProcessor):
    """
    Processor for creating new weather subscriptions.
    Handles subscription creation with location validation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateSubscriptionProcessor",
            description="Creates new weather subscription with location validation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscription creation according to functional requirements.

        Args:
            entity: The WeatherSubscription entity to create
            **kwargs: Additional processing parameters

        Returns:
            The created subscription entity
        """
        try:
            self.logger.info(
                f"Creating subscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Set default values if not provided
            if not subscription.frequency:
                subscription.frequency = "daily"

            # Set subscription as active by default
            subscription.active = True

            # Update timestamp
            subscription.update_timestamp()

            self.logger.info(
                f"Subscription {subscription.technical_id} created successfully for location {subscription.location}"
            )

            return subscription

        except Exception as e:
            self.logger.error(
                f"Error creating subscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class ActivateSubscriptionProcessor(CyodaProcessor):
    """
    Processor for activating weather subscriptions.
    Enables subscription for weather data fetching and notifications.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateSubscriptionProcessor",
            description="Activates subscription for weather data fetching and notifications",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscription activation according to functional requirements.

        Args:
            entity: The WeatherSubscription entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated subscription entity
        """
        try:
            self.logger.info(
                f"Activating subscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Activate subscription
            subscription.activate()

            self.logger.info(
                f"Subscription {subscription.technical_id} activated successfully"
            )

            return subscription

        except Exception as e:
            self.logger.error(
                f"Error activating subscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class PauseSubscriptionProcessor(CyodaProcessor):
    """
    Processor for pausing weather subscriptions.
    Temporarily disables subscription without deleting it.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PauseSubscriptionProcessor",
            description="Temporarily disables subscription without deleting it",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscription pausing according to functional requirements.

        Args:
            entity: The WeatherSubscription entity to pause
            **kwargs: Additional processing parameters

        Returns:
            The paused subscription entity
        """
        try:
            self.logger.info(
                f"Pausing subscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Pause subscription
            subscription.pause()

            self.logger.info(
                f"Subscription {subscription.technical_id} paused successfully"
            )

            return subscription

        except Exception as e:
            self.logger.error(
                f"Error pausing subscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class ResumeSubscriptionProcessor(CyodaProcessor):
    """
    Processor for resuming paused weather subscriptions.
    Reactivates paused subscription.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ResumeSubscriptionProcessor",
            description="Reactivates paused subscription",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscription resumption according to functional requirements.

        Args:
            entity: The WeatherSubscription entity to resume
            **kwargs: Additional processing parameters

        Returns:
            The resumed subscription entity
        """
        try:
            self.logger.info(
                f"Resuming subscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Resume subscription
            subscription.resume()

            self.logger.info(
                f"Subscription {subscription.technical_id} resumed successfully"
            )

            return subscription

        except Exception as e:
            self.logger.error(
                f"Error resuming subscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class CancelSubscriptionProcessor(CyodaProcessor):
    """
    Processor for cancelling weather subscriptions.
    Permanently cancels subscription and stops all related activities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CancelSubscriptionProcessor",
            description="Permanently cancels subscription and stops all related activities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process subscription cancellation according to functional requirements.

        Args:
            entity: The WeatherSubscription entity to cancel
            **kwargs: Additional processing parameters

        Returns:
            The cancelled subscription entity
        """
        try:
            self.logger.info(
                f"Cancelling subscription {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Cancel related weather data fetching
            await self._cancel_related_weather_data(subscription.get_id())

            # Deactivate subscription
            subscription.deactivate()

            self.logger.info(
                f"Subscription {subscription.technical_id} cancelled successfully"
            )

            return subscription

        except Exception as e:
            self.logger.error(
                f"Error cancelling subscription {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_related_weather_data(self, subscription_id: str) -> None:
        """
        Cancel related weather data fetching for a subscription.

        Args:
            subscription_id: The subscription ID whose weather data to cancel
        """
        try:
            entity_service = get_entity_service()

            # Find all active weather data for this subscription
            # Note: This would require implementing a search for WeatherData entities
            # For now, we'll log the intent - the actual implementation would depend on
            # the WeatherData entity being available

            self.logger.info(
                f"Cancelling weather data fetching for subscription {subscription_id}"
            )

            # TODO: Implement weather data cancellation when WeatherData processors are available
            # This would involve:
            # 1. Search for all WeatherData entities with subscription_id = subscription_id
            # 2. For each weather data, trigger the expire_data transition if in active states

        except Exception as e:
            self.logger.error(
                f"Failed to cancel weather data for subscription {subscription_id}: {str(e)}"
            )
            # Continue with subscription cancellation even if weather data cancellation fails
            # This ensures subscription cancellation is not blocked by weather data issues
