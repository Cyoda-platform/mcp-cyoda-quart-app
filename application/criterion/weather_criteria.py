"""
Weather-related Criteria Checkers for Cyoda Client Application

Implements criteria checkers for validating weather subscriptions, weather data,
email recipients, and retry limits as specified in workflow definitions.
"""

import logging
from typing import Any

from application.entity.emailnotification.version_1.email_notification import (
    EmailNotification,
)
from application.entity.user.version_1.user import User
from application.entity.weatherdata.version_1.weather_data import WeatherData
from application.entity.weathersubscription.version_1.weather_subscription import (
    WeatherSubscription,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class ValidLocationCriteria(CyodaCriteriaChecker):
    """
    Validation criteria for WeatherSubscription location data.
    Checks if location coordinates are valid and subscription is properly configured.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidLocationCriteria",
            description="Validates WeatherSubscription location coordinates and configuration",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the subscription has valid location data.

        Args:
            entity: The CyodaEntity to validate (expected to be WeatherSubscription)
            **kwargs: Additional criteria parameters

        Returns:
            True if the subscription has valid location data, False otherwise
        """
        try:
            self.logger.info(
                f"Validating location for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherSubscription for type-safe operations
            subscription = cast_entity(entity, WeatherSubscription)

            # Validate location name
            if not subscription.location or len(subscription.location.strip()) < 3:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid location name: '{subscription.location}'"
                )
                return False

            # Validate latitude (must be between -90 and 90)
            if subscription.latitude < -90.0 or subscription.latitude > 90.0:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid latitude: {subscription.latitude}"
                )
                return False

            # Validate longitude (must be between -180 and 180)
            if subscription.longitude < -180.0 or subscription.longitude > 180.0:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid longitude: {subscription.longitude}"
                )
                return False

            # Validate user_id exists
            if not subscription.user_id or len(subscription.user_id.strip()) == 0:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid user_id"
                )
                return False

            # Validate frequency
            if subscription.frequency not in subscription.ALLOWED_FREQUENCIES:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid frequency: {subscription.frequency}"
                )
                return False

            # Check if associated user exists and is active
            user_is_valid = await self._validate_associated_user(subscription.user_id)
            if not user_is_valid:
                self.logger.warning(
                    f"Subscription {subscription.technical_id} has invalid or inactive user: {subscription.user_id}"
                )
                return False

            self.logger.info(
                f"Subscription {subscription.technical_id} passed location validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating location for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _validate_associated_user(self, user_id: str) -> bool:
        """
        Validate that the associated user exists and is active.

        Args:
            user_id: The user ID to validate

        Returns:
            True if user exists and is active, False otherwise
        """
        try:
            entity_service = get_entity_service()

            # TODO: Implement user lookup when User entity service integration is available
            # For now, assume user is valid if user_id is provided
            self.logger.info(f"Validating user {user_id} (simulated)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate user {user_id}: {str(e)}")
            return False


class ValidWeatherDataCriteria(CyodaCriteriaChecker):
    """
    Validation criteria for WeatherData processing.
    Checks if weather data is complete and valid for processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidWeatherDataCriteria",
            description="Validates WeatherData completeness and validity for processing",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the weather data is valid for processing.

        Args:
            entity: The CyodaEntity to validate (expected to be WeatherData)
            **kwargs: Additional criteria parameters

        Returns:
            True if the weather data is valid, False otherwise
        """
        try:
            self.logger.info(
                f"Validating weather data for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Validate required fields are present
            if (
                not weather_data.subscription_id
                or len(weather_data.subscription_id.strip()) == 0
            ):
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid subscription_id"
                )
                return False

            if not weather_data.location or len(weather_data.location.strip()) < 3:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid location"
                )
                return False

            # Validate coordinates
            if weather_data.latitude < -90.0 or weather_data.latitude > 90.0:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid latitude: {weather_data.latitude}"
                )
                return False

            if weather_data.longitude < -180.0 or weather_data.longitude > 180.0:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid longitude: {weather_data.longitude}"
                )
                return False

            # Validate weather values are reasonable
            if weather_data.temperature < -100.0 or weather_data.temperature > 100.0:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has unreasonable temperature: {weather_data.temperature}"
                )
                return False

            if weather_data.humidity < 0.0 or weather_data.humidity > 100.0:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid humidity: {weather_data.humidity}"
                )
                return False

            if weather_data.wind_speed < 0.0 or weather_data.wind_speed > 500.0:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid wind speed: {weather_data.wind_speed}"
                )
                return False

            if (
                not weather_data.weather_condition
                or len(weather_data.weather_condition.strip()) == 0
            ):
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has invalid weather condition"
                )
                return False

            # Validate timestamps
            if not weather_data.fetch_timestamp:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has missing fetch timestamp"
                )
                return False

            if not weather_data.forecast_date:
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} has missing forecast date"
                )
                return False

            # Check if data is not expired
            if weather_data.is_expired():
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} is expired"
                )
                return False

            self.logger.info(
                f"Weather data {weather_data.technical_id} passed validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating weather data for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False


class ValidRecipientCriteria(CyodaCriteriaChecker):
    """
    Validation criteria for EmailNotification recipients.
    Checks if recipient is valid and eligible to receive notifications.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidRecipientCriteria",
            description="Validates EmailNotification recipient eligibility",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the email notification has a valid recipient.

        Args:
            entity: The CyodaEntity to validate (expected to be EmailNotification)
            **kwargs: Additional criteria parameters

        Returns:
            True if the recipient is valid, False otherwise
        """
        try:
            self.logger.info(
                f"Validating recipient for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Validate recipient email format (already done by entity validation)
            if (
                not notification.recipient_email
                or len(notification.recipient_email.strip()) == 0
            ):
                self.logger.warning(
                    f"Notification {notification.technical_id} has invalid recipient email"
                )
                return False

            # Validate user_id exists
            if not notification.user_id or len(notification.user_id.strip()) == 0:
                self.logger.warning(
                    f"Notification {notification.technical_id} has invalid user_id"
                )
                return False

            # Check if associated user is active and eligible for notifications
            user_is_eligible = await self._validate_user_eligibility(
                notification.user_id
            )
            if not user_is_eligible:
                self.logger.warning(
                    f"Notification {notification.technical_id} user is not eligible: {notification.user_id}"
                )
                return False

            # Validate content is present
            if not notification.subject or len(notification.subject.strip()) == 0:
                self.logger.warning(
                    f"Notification {notification.technical_id} has invalid subject"
                )
                return False

            if not notification.content or len(notification.content.strip()) == 0:
                self.logger.warning(
                    f"Notification {notification.technical_id} has invalid content"
                )
                return False

            self.logger.info(
                f"Notification {notification.technical_id} passed recipient validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating recipient for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _validate_user_eligibility(self, user_id: str) -> bool:
        """
        Validate that the user is eligible to receive notifications.

        Args:
            user_id: The user ID to validate

        Returns:
            True if user is eligible, False otherwise
        """
        try:
            entity_service = get_entity_service()

            # TODO: Implement user eligibility check when User entity service integration is available
            # This would check if user is active and in a state that allows notifications
            self.logger.info(f"Validating user eligibility {user_id} (simulated)")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to validate user eligibility {user_id}: {str(e)}"
            )
            return False


class MaxRetriesCriteria(CyodaCriteriaChecker):
    """
    Validation criteria for EmailNotification retry limits.
    Checks if maximum retry attempts have been reached.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MaxRetriesCriteria",
            description="Validates EmailNotification retry count against maximum attempts",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the email notification has reached maximum retry attempts.

        Args:
            entity: The CyodaEntity to validate (expected to be EmailNotification)
            **kwargs: Additional criteria parameters

        Returns:
            True if maximum retries reached, False otherwise
        """
        try:
            self.logger.info(
                f"Validating retry count for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            notification = cast_entity(entity, EmailNotification)

            # Check if maximum retry attempts have been reached
            max_retries_reached = (
                notification.retry_count >= notification.MAX_RETRY_ATTEMPTS
            )

            if max_retries_reached:
                self.logger.info(
                    f"Notification {notification.technical_id} has reached maximum retries "
                    f"({notification.retry_count}/{notification.MAX_RETRY_ATTEMPTS})"
                )
            else:
                self.logger.info(
                    f"Notification {notification.technical_id} retry count is within limits "
                    f"({notification.retry_count}/{notification.MAX_RETRY_ATTEMPTS})"
                )

            return max_retries_reached

        except Exception as e:
            self.logger.error(
                f"Error validating retry count for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
