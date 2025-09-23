"""
WeatherDataProcessor for Weather Data Application

Handles processing of WeatherData entities by fetching weather observations
from MSC GeoMet API and enriching weather data with additional calculations.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.weather_data.version_1.weather_data import WeatherData
from services.services import get_entity_service


class WeatherDataProcessor(CyodaProcessor):
    """
    Processor for WeatherData that fetches weather observations from MSC GeoMet API
    and enriches weather data with calculations and analysis.
    """

    def __init__(self) -> None:
        super().__init__(
            name="WeatherDataProcessor",
            description="Processes WeatherData entities by fetching observations from MSC GeoMet API",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        self.msc_geomet_base_url = "https://api.weather.gc.ca"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the WeatherData by fetching observations from MSC GeoMet API.

        Args:
            entity: The WeatherData to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing WeatherData {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherData for type-safe operations
            weather_data = cast_entity(entity, WeatherData)

            # Fetch weather observations from MSC GeoMet API
            observations = await self._fetch_weather_observations(
                weather_data.station_id, 
                weather_data.observation_date
            )
            
            if observations:
                # Enrich weather data with observations
                self._enrich_weather_data(weather_data, observations)
                
                # Calculate additional metrics
                processed_data = self._calculate_weather_metrics(weather_data)
                weather_data.set_processed_data(processed_data)
                
                self.logger.info(
                    f"Successfully enriched WeatherData for station {weather_data.station_id} on {weather_data.observation_date}"
                )
            else:
                # Mark as processed but with limited data
                processed_data = {
                    "processed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "data_source": "manual_entry",
                    "enrichment_status": "no_api_data",
                    "completeness_score": weather_data.get_data_completeness_score()
                }
                weather_data.set_processed_data(processed_data)
                
                self.logger.warning(
                    f"No API data found for station {weather_data.station_id} on {weather_data.observation_date}"
                )

            # Log processing completion
            self.logger.info(
                f"WeatherData {weather_data.technical_id} processed successfully"
            )

            return weather_data

        except Exception as e:
            self.logger.error(
                f"Error processing WeatherData {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_weather_observations(
        self, station_id: str, observation_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch weather observations from MSC GeoMet API.

        Args:
            station_id: The station identifier
            observation_date: The observation date (YYYY-MM-DD)

        Returns:
            Weather observations dictionary or None if not found
        """
        try:
            # Try to fetch from climate-daily collection
            url = f"{self.msc_geomet_base_url}/collections/climate-daily/items"
            params = {
                "f": "json",
                "limit": 10,
                "station_id": station_id,
                "datetime": f"{observation_date}T00:00:00Z/{observation_date}T23:59:59Z"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        features = data.get("features", [])
                        
                        if features:
                            # Find the observation for the specific date
                            for feature in features:
                                properties = feature.get("properties", {})
                                if properties.get("date") == observation_date:
                                    return {
                                        "properties": properties,
                                        "source": "climate-daily"
                                    }
                    else:
                        self.logger.warning(
                            f"MSC GeoMet API returned status {response.status} for station {station_id} on {observation_date}"
                        )

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching weather data for station {station_id} on {observation_date}")
        except Exception as e:
            self.logger.error(f"Error fetching weather data for {station_id} on {observation_date}: {str(e)}")

        return None

    def _enrich_weather_data(self, weather_data: WeatherData, api_data: Dict[str, Any]) -> None:
        """
        Enrich weather data with observations from MSC GeoMet API.

        Args:
            weather_data: The WeatherData entity to enrich
            api_data: Data from MSC GeoMet API
        """
        properties = api_data.get("properties", {})
        
        # Map API fields to entity fields
        field_mapping = {
            "temp_max": "temperature_max",
            "temp_min": "temperature_min", 
            "temp_mean": "temperature_mean",
            "total_precip": "precipitation_total",
            "rain": "rain_total",
            "snow": "snow_total",
            "wind_speed": "wind_speed",
            "pressure_sea_level": "pressure_sea_level",
            "pressure_station": "pressure_station"
        }
        
        # Update weather data fields if they're not already set
        for api_field, entity_field in field_mapping.items():
            api_value = properties.get(api_field)
            if api_value is not None and getattr(weather_data, entity_field) is None:
                try:
                    # Convert to float if it's a numeric value
                    if isinstance(api_value, (int, float, str)):
                        setattr(weather_data, entity_field, float(api_value))
                        self.logger.debug(f"Updated {entity_field} with value {api_value}")
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not convert {api_field} value '{api_value}' to float")

        # Set data quality based on API source
        weather_data.data_quality = "API_VERIFIED"
        weather_data.update_timestamp()

    def _calculate_weather_metrics(self, weather_data: WeatherData) -> Dict[str, Any]:
        """
        Calculate additional weather metrics and analysis.

        Args:
            weather_data: The WeatherData entity

        Returns:
            Dictionary containing calculated metrics
        """
        current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        metrics = {
            "processed_at": current_timestamp,
            "data_source": "msc_geomet_api",
            "enrichment_status": "success",
            "completeness_score": weather_data.get_data_completeness_score()
        }
        
        # Calculate temperature range if both min and max are available
        if weather_data.temperature_max is not None and weather_data.temperature_min is not None:
            metrics["temperature_range"] = weather_data.temperature_max - weather_data.temperature_min
            
        # Classify precipitation type
        if weather_data.precipitation_total is not None:
            if weather_data.snow_total is not None and weather_data.snow_total > 0:
                if weather_data.rain_total is not None and weather_data.rain_total > 0:
                    metrics["precipitation_type"] = "mixed"
                else:
                    metrics["precipitation_type"] = "snow"
            elif weather_data.rain_total is not None and weather_data.rain_total > 0:
                metrics["precipitation_type"] = "rain"
            else:
                metrics["precipitation_type"] = "other"
        
        # Classify weather conditions
        conditions = []
        if weather_data.temperature_max is not None:
            if weather_data.temperature_max >= 30:
                conditions.append("hot")
            elif weather_data.temperature_max <= 0:
                conditions.append("freezing")
                
        if weather_data.precipitation_total is not None and weather_data.precipitation_total > 10:
            conditions.append("wet")
            
        if weather_data.wind_speed is not None and weather_data.wind_speed > 50:
            conditions.append("windy")
            
        metrics["weather_conditions"] = conditions
        
        return metrics
