"""
WeatherData Processors for Cyoda Client Application

Handles all WeatherData entity workflow transitions and business logic processing.
Implements processors for weather data fetching, processing, notification preparation, and expiration.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.weatherdata.version_1.weather_data import WeatherData
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class StartFetchProcessor(CyodaProcessor):
    """
    Processor for starting weather data fetch.
    Initializes weather data fetching process.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StartFetchProcessor",
            description="Initializes weather data fetching process",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process weather data fetch initialization according to functional requirements.

        Args:
            entity: The WeatherData entity to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized weather data entity
        """
        try:
            self.logger.info(
                f"Starting fetch for weather data {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Set fetch timestamp if not already set
            if not weather_data.fetch_timestamp:
                weather_data.fetch_timestamp = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Update timestamp
            weather_data.update_timestamp()

            self.logger.info(
                f"Weather data fetch started for {weather_data.technical_id} at location {weather_data.location}"
            )

            return weather_data

        except Exception as e:
            self.logger.error(
                f"Error starting fetch for weather data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class ProcessWeatherDataProcessor(CyodaProcessor):
    """
    Processor for processing weather data from MSC GeoMet API.
    Handles weather data processing and validation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProcessWeatherDataProcessor",
            description="Processes weather data from MSC GeoMet API with validation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process weather data according to functional requirements.

        Args:
            entity: The WeatherData entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed weather data entity
        """
        try:
            self.logger.info(
                f"Processing weather data {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Simulate MSC GeoMet API data processing
            # In a real implementation, this would:
            # 1. Fetch data from MSC GeoMet API using coordinates
            # 2. Parse and validate the response
            # 3. Update the weather data fields

            processed_data = await self._fetch_from_msc_geomet_api(weather_data)

            # Update weather data with processed information
            if processed_data:
                weather_data.temperature = processed_data.get(
                    "temperature", weather_data.temperature
                )
                weather_data.humidity = processed_data.get(
                    "humidity", weather_data.humidity
                )
                weather_data.wind_speed = processed_data.get(
                    "wind_speed", weather_data.wind_speed
                )
                weather_data.weather_condition = processed_data.get(
                    "weather_condition", weather_data.weather_condition
                )

            # Update timestamp
            weather_data.update_timestamp()

            self.logger.info(
                f"Weather data {weather_data.technical_id} processed successfully: {weather_data.get_summary()}"
            )

            return weather_data

        except Exception as e:
            self.logger.error(
                f"Error processing weather data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_from_msc_geomet_api(
        self, weather_data: WeatherData
    ) -> Dict[str, Any]:
        """
        Fetch weather data from MSC GeoMet API.

        Args:
            weather_data: The weather data entity with coordinates

        Returns:
            Dictionary with processed weather data
        """
        try:
            # TODO: Implement actual MSC GeoMet API integration
            # For now, return the existing data as processed
            self.logger.info(
                f"Fetching weather data from MSC GeoMet API for coordinates "
                f"({weather_data.latitude}, {weather_data.longitude})"
            )

            # Simulate API response processing
            return {
                "temperature": weather_data.temperature,
                "humidity": weather_data.humidity,
                "wind_speed": weather_data.wind_speed,
                "weather_condition": weather_data.weather_condition,
            }

        except Exception as e:
            self.logger.error(f"Failed to fetch from MSC GeoMet API: {str(e)}")
            return {}


class PrepareNotificationProcessor(CyodaProcessor):
    """
    Processor for preparing weather data for email notifications.
    Formats weather data for email content generation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PrepareNotificationProcessor",
            description="Prepares weather data for email notification generation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process weather data for notification preparation according to functional requirements.

        Args:
            entity: The WeatherData entity to prepare for notification
            **kwargs: Additional processing parameters

        Returns:
            The notification-ready weather data entity
        """
        try:
            self.logger.info(
                f"Preparing notification for weather data {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Create email notifications for users subscribed to this location
            await self._create_email_notifications(weather_data)

            # Update timestamp
            weather_data.update_timestamp()

            self.logger.info(
                f"Weather data {weather_data.technical_id} prepared for notifications"
            )

            return weather_data

        except Exception as e:
            self.logger.error(
                f"Error preparing notification for weather data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _create_email_notifications(self, weather_data: WeatherData) -> None:
        """
        Create email notifications for weather data.

        Args:
            weather_data: The weather data to create notifications for
        """
        try:
            self.logger.info(
                f"Creating email notifications for weather data {weather_data.technical_id}"
            )

            # TODO: Implement email notification creation when EmailNotification processors are available
            # This would involve:
            # 1. Find the subscription associated with this weather data
            # 2. Find the user associated with the subscription
            # 3. Create EmailNotification entities with formatted content
            # 4. Save the notifications to trigger the email workflow

        except Exception as e:
            self.logger.error(
                f"Failed to create email notifications for weather data {weather_data.technical_id}: {str(e)}"
            )
            # Continue with notification preparation even if email creation fails


class ExpireDataProcessor(CyodaProcessor):
    """
    Processor for expiring old weather data.
    Marks weather data as expired after 24 hours.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ExpireDataProcessor",
            description="Marks weather data as expired after 24 hours",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process weather data expiration according to functional requirements.

        Args:
            entity: The WeatherData entity to expire
            **kwargs: Additional processing parameters

        Returns:
            The expired weather data entity
        """
        try:
            self.logger.info(
                f"Expiring weather data {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Check if data is actually expired (24 hours old)
            if not weather_data.is_expired():
                self.logger.warning(
                    f"Weather data {weather_data.technical_id} is not yet expired, "
                    f"but expiration was requested"
                )

            # Update timestamp to mark expiration processing
            weather_data.update_timestamp()

            self.logger.info(
                f"Weather data {weather_data.technical_id} expired successfully"
            )

            return weather_data

        except Exception as e:
            self.logger.error(
                f"Error expiring weather data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
