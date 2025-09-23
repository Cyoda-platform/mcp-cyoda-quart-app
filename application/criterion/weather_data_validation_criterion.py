"""
WeatherDataValidationCriterion for Weather Data Application

Validates that WeatherData meets all required business rules and data quality
standards before it can proceed to processing stage.
"""

from datetime import datetime
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.weather_data.version_1.weather_data import WeatherData


class WeatherDataValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for WeatherData that checks data quality and completeness
    before the data can proceed to processing stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="WeatherDataValidationCriterion",
            description="Validates WeatherData quality and completeness requirements",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the weather data meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be WeatherData)
            **kwargs: Additional criteria parameters

        Returns:
            True if the data meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating WeatherData {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Validate required fields
            if not weather_data.station_id or len(weather_data.station_id.strip()) == 0:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has invalid station_id: '{weather_data.station_id}'"
                )
                return False

            if not weather_data.observation_date:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has missing observation_date"
                )
                return False

            # Validate observation date format and reasonableness
            try:
                obs_date = datetime.strptime(weather_data.observation_date, "%Y-%m-%d")
                current_date = datetime.now()
                
                # Check if date is not in the future
                if obs_date.date() > current_date.date():
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has future observation_date: {weather_data.observation_date}"
                    )
                    return False
                
                # Check if date is not too old (before 1800)
                if obs_date.year < 1800:
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has unrealistic observation_date: {weather_data.observation_date}"
                    )
                    return False
                    
            except ValueError:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has invalid observation_date format: {weather_data.observation_date}"
                )
                return False

            # Validate temperature data if present
            if not self._validate_temperature_data(weather_data):
                return False

            # Validate precipitation data if present
            if not self._validate_precipitation_data(weather_data):
                return False

            # Validate wind data if present
            if not self._validate_wind_data(weather_data):
                return False

            # Validate pressure data if present
            if not self._validate_pressure_data(weather_data):
                return False

            # Check minimum data completeness
            if not self._check_minimum_data_completeness(weather_data):
                return False

            self.logger.info(
                f"WeatherData {weather_data.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating WeatherData {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_temperature_data(self, weather_data: WeatherData) -> bool:
        """Validate temperature measurements."""
        # Check temperature ranges (reasonable for Canada)
        temp_fields = [
            ("temperature_max", weather_data.temperature_max),
            ("temperature_min", weather_data.temperature_min),
            ("temperature_mean", weather_data.temperature_mean)
        ]
        
        for field_name, temp_value in temp_fields:
            if temp_value is not None:
                if temp_value < -60 or temp_value > 60:
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has unrealistic {field_name}: {temp_value}°C"
                    )
                    return False

        # Check temperature consistency if multiple values present
        if (weather_data.temperature_max is not None and 
            weather_data.temperature_min is not None):
            if weather_data.temperature_max < weather_data.temperature_min:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has max temp ({weather_data.temperature_max}) less than min temp ({weather_data.temperature_min})"
                )
                return False

        # Check mean temperature is between min and max if all are present
        if (weather_data.temperature_max is not None and 
            weather_data.temperature_min is not None and
            weather_data.temperature_mean is not None):
            if not (weather_data.temperature_min <= weather_data.temperature_mean <= weather_data.temperature_max):
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has mean temp ({weather_data.temperature_mean}) outside min-max range"
                )
                return False

        return True

    def _validate_precipitation_data(self, weather_data: WeatherData) -> bool:
        """Validate precipitation measurements."""
        precip_fields = [
            ("precipitation_total", weather_data.precipitation_total),
            ("rain_total", weather_data.rain_total),
            ("snow_total", weather_data.snow_total)
        ]
        
        for field_name, precip_value in precip_fields:
            if precip_value is not None:
                if precip_value < 0:
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has negative {field_name}: {precip_value}mm"
                    )
                    return False
                
                # Check for unrealistic daily precipitation (>500mm is extremely rare)
                if precip_value > 500:
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has unrealistic {field_name}: {precip_value}mm"
                    )
                    return False

        # Check precipitation consistency
        if (weather_data.precipitation_total is not None and
            weather_data.rain_total is not None and
            weather_data.snow_total is not None):
            total_components = weather_data.rain_total + weather_data.snow_total
            # Allow some tolerance for measurement differences
            if abs(weather_data.precipitation_total - total_components) > 5:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has inconsistent precipitation totals"
                )
                return False

        return True

    def _validate_wind_data(self, weather_data: WeatherData) -> bool:
        """Validate wind measurements."""
        if weather_data.wind_speed is not None:
            if weather_data.wind_speed < 0:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has negative wind_speed: {weather_data.wind_speed}"
                )
                return False
            
            # Check for unrealistic wind speeds (>200 km/h is extremely rare)
            if weather_data.wind_speed > 200:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has unrealistic wind_speed: {weather_data.wind_speed} km/h"
                )
                return False

        if weather_data.wind_direction is not None:
            if weather_data.wind_direction < 0 or weather_data.wind_direction >= 360:
                self.logger.warning(
                    f"WeatherData {weather_data.technical_id} has invalid wind_direction: {weather_data.wind_direction}°"
                )
                return False

        return True

    def _validate_pressure_data(self, weather_data: WeatherData) -> bool:
        """Validate pressure measurements."""
        pressure_fields = [
            ("pressure_sea_level", weather_data.pressure_sea_level),
            ("pressure_station", weather_data.pressure_station)
        ]
        
        for field_name, pressure_value in pressure_fields:
            if pressure_value is not None:
                # Reasonable pressure range in kPa (roughly 85-105 kPa)
                if pressure_value < 85 or pressure_value > 105:
                    self.logger.warning(
                        f"WeatherData {weather_data.technical_id} has unrealistic {field_name}: {pressure_value} kPa"
                    )
                    return False

        return True

    def _check_minimum_data_completeness(self, weather_data: WeatherData) -> bool:
        """Check if weather data has minimum required completeness."""
        # Require at least one temperature measurement OR one precipitation measurement
        has_temperature = weather_data.has_temperature_data()
        has_precipitation = weather_data.has_precipitation_data()
        
        if not has_temperature and not has_precipitation:
            self.logger.warning(
                f"WeatherData {weather_data.technical_id} lacks minimum data (no temperature or precipitation data)"
            )
            return False

        # Check overall completeness score
        completeness_score = weather_data.get_data_completeness_score()
        if completeness_score < 0.1:  # At least 10% of fields should be populated
            self.logger.warning(
                f"WeatherData {weather_data.technical_id} has insufficient data completeness: {completeness_score:.2%}"
            )
            return False

        return True
