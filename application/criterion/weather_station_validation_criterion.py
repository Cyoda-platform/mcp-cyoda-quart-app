"""
WeatherStationValidationCriterion for Weather Data Application

Validates that a WeatherStation meets all required business rules before it can
proceed to the active stage.
"""

from typing import Any

from application.entity.weather_station.version_1.weather_station import WeatherStation
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class WeatherStationValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for WeatherStation that checks all business rules
    before the station can proceed to active stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="WeatherStationValidationCriterion",
            description="Validates WeatherStation business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the weather station meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be WeatherStation)
            **kwargs: Additional criteria parameters

        Returns:
            True if the station meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating WeatherStation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherStation for type-safe operations
            weather_station = cast_entity(entity, WeatherStation)

            # Validate required fields
            if (
                not weather_station.station_id
                or len(weather_station.station_id.strip()) == 0
            ):
                self.logger.warning(
                    f"Station {weather_station.technical_id} has invalid station_id: '{weather_station.station_id}'"
                )
                return False

            if (
                not weather_station.station_name
                or len(weather_station.station_name.strip()) == 0
            ):
                self.logger.warning(
                    f"Station {weather_station.technical_id} has invalid station_name: '{weather_station.station_name}'"
                )
                return False

            # Validate geographic coordinates
            if weather_station.latitude < -90 or weather_station.latitude > 90:
                self.logger.warning(
                    f"Station {weather_station.technical_id} has invalid latitude: {weather_station.latitude}"
                )
                return False

            if weather_station.longitude < -180 or weather_station.longitude > 180:
                self.logger.warning(
                    f"Station {weather_station.technical_id} has invalid longitude: {weather_station.longitude}"
                )
                return False

            # Validate Canadian coordinates (rough bounds for Canada)
            if not self._is_in_canada(
                weather_station.latitude, weather_station.longitude
            ):
                self.logger.warning(
                    f"Station {weather_station.technical_id} coordinates ({weather_station.latitude}, {weather_station.longitude}) appear to be outside Canada"
                )
                return False

            # Validate elevation if provided
            if weather_station.elevation is not None:
                if weather_station.elevation < -500 or weather_station.elevation > 6000:
                    self.logger.warning(
                        f"Station {weather_station.technical_id} has unrealistic elevation: {weather_station.elevation}m"
                    )
                    return False

            # Validate data years if provided
            if (
                weather_station.first_year is not None
                and weather_station.last_year is not None
            ):
                if weather_station.first_year > weather_station.last_year:
                    self.logger.warning(
                        f"Station {weather_station.technical_id} has first_year ({weather_station.first_year}) after last_year ({weather_station.last_year})"
                    )
                    return False

                # Check if years are reasonable
                current_year = (
                    2024  # Could use datetime.now().year but keeping it simple
                )
                if (
                    weather_station.first_year < 1800
                    or weather_station.first_year > current_year
                ):
                    self.logger.warning(
                        f"Station {weather_station.technical_id} has unrealistic first_year: {weather_station.first_year}"
                    )
                    return False

                if (
                    weather_station.last_year < 1800
                    or weather_station.last_year > current_year
                ):
                    self.logger.warning(
                        f"Station {weather_station.technical_id} has unrealistic last_year: {weather_station.last_year}"
                    )
                    return False

            # Validate province if provided
            if weather_station.province:
                valid_provinces = [
                    "Alberta",
                    "British Columbia",
                    "Manitoba",
                    "New Brunswick",
                    "Newfoundland and Labrador",
                    "Northwest Territories",
                    "Nova Scotia",
                    "Nunavut",
                    "Ontario",
                    "Prince Edward Island",
                    "Quebec",
                    "Saskatchewan",
                    "Yukon",
                    "AB",
                    "BC",
                    "MB",
                    "NB",
                    "NL",
                    "NT",
                    "NS",
                    "NU",
                    "ON",
                    "PE",
                    "QC",
                    "SK",
                    "YT",
                ]
                if weather_station.province not in valid_provinces:
                    self.logger.warning(
                        f"Station {weather_station.technical_id} has unrecognized province: '{weather_station.province}'"
                    )
                    # Don't fail validation for this, just log warning

            self.logger.info(
                f"WeatherStation {weather_station.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating WeatherStation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _is_in_canada(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are roughly within Canada's bounds.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees

        Returns:
            True if coordinates are within Canada's approximate bounds
        """
        # Rough bounding box for Canada
        # These are approximate bounds and include some buffer
        canada_bounds = {
            "min_lat": 41.0,  # Southern Ontario
            "max_lat": 84.0,  # Northern islands
            "min_lon": -141.0,  # Yukon border with Alaska
            "max_lon": -52.0,  # Newfoundland
        }

        return (
            canada_bounds["min_lat"] <= latitude <= canada_bounds["max_lat"]
            and canada_bounds["min_lon"] <= longitude <= canada_bounds["max_lon"]
        )
