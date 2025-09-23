"""
WeatherStationProcessor for Weather Data Application

Handles processing of WeatherStation entities by fetching station metadata
from MSC GeoMet API and enriching station information.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientTimeout

from application.entity.weather_station.version_1.weather_station import WeatherStation
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class WeatherStationProcessor(CyodaProcessor):
    """
    Processor for WeatherStation that fetches station data from MSC GeoMet API
    and enriches station metadata.
    """

    def __init__(self) -> None:
        super().__init__(
            name="WeatherStationProcessor",
            description="Processes WeatherStation entities by fetching data from MSC GeoMet API",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        self.msc_geomet_base_url = "https://api.weather.gc.ca"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the WeatherStation by fetching additional data from MSC GeoMet API.

        Args:
            entity: The WeatherStation to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing WeatherStation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to WeatherStation for type-safe operations
            weather_station = cast_entity(entity, WeatherStation)

            # Fetch additional station data from MSC GeoMet API
            station_data = await self._fetch_station_data(weather_station.station_id)

            if station_data:
                # Enrich station with additional metadata
                self._enrich_station_data(weather_station, station_data)

                # Update fetch status
                weather_station.set_data_fetch_status(
                    "SUCCESS",
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                )
            else:
                # Mark as failed but don't fail the processing
                weather_station.set_data_fetch_status("FAILED")
                self.logger.warning(
                    f"Could not fetch additional data for station {weather_station.station_id}"
                )

            # Log processing completion
            self.logger.info(
                f"WeatherStation {weather_station.technical_id} processed successfully"
            )

            return weather_station

        except Exception as e:
            self.logger.error(
                f"Error processing WeatherStation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Set failed status but don't re-raise to avoid workflow failure
            if hasattr(entity, "set_data_fetch_status"):
                entity.set_data_fetch_status("ERROR")
            return entity

    async def _fetch_station_data(self, station_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch station data from MSC GeoMet API.

        Args:
            station_id: The station identifier to fetch data for

        Returns:
            Station data dictionary or None if not found
        """
        try:
            # Try to fetch from climate-stations collection
            url = f"{self.msc_geomet_base_url}/collections/climate-stations/items"
            params = {"f": "json", "limit": "10", "station_id": station_id}

            timeout = ClientTimeout(total=30)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        features = data.get("features", [])

                        if features:
                            # Return the first matching station
                            station_feature = features[0]
                            properties = station_feature.get("properties", {})
                            geometry = station_feature.get("geometry", {})

                            return {
                                "properties": properties,
                                "geometry": geometry,
                                "source": "climate-stations",
                            }
                    else:
                        self.logger.warning(
                            f"MSC GeoMet API returned status {response.status} for station {station_id}"
                        )

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching data for station {station_id}")
        except Exception as e:
            self.logger.error(f"Error fetching station data for {station_id}: {str(e)}")

        return None

    def _enrich_station_data(
        self, station: WeatherStation, api_data: Dict[str, Any]
    ) -> None:
        """
        Enrich station with data from MSC GeoMet API.

        Args:
            station: The WeatherStation entity to enrich
            api_data: Data from MSC GeoMet API
        """
        properties = api_data.get("properties", {})
        geometry = api_data.get("geometry", {})

        # Update location if available and more precise
        if geometry.get("coordinates"):
            coords = geometry["coordinates"]
            if len(coords) >= 2:
                # GeoJSON uses [longitude, latitude] format
                api_longitude, api_latitude = coords[0], coords[1]

                # Update if we don't have coordinates or if API data is more precise
                if (
                    abs(station.latitude - api_latitude) > 0.001
                    or abs(station.longitude - api_longitude) > 0.001
                ):
                    station.latitude = api_latitude
                    station.longitude = api_longitude
                    self.logger.info(
                        f"Updated coordinates for station {station.station_id}"
                    )

                # Update elevation if available
                if len(coords) >= 3:
                    station.elevation = coords[2]

        # Update station metadata from properties
        if properties.get("station_name") and not station.station_name:
            station.station_name = properties["station_name"]

        if properties.get("province") and not station.province:
            station.province = properties["province"]

        if properties.get("first_year"):
            try:
                station.first_year = int(properties["first_year"])
            except (ValueError, TypeError):
                pass

        if properties.get("last_year"):
            try:
                station.last_year = int(properties["last_year"])
            except (ValueError, TypeError):
                pass

        # Update station type if available
        if properties.get("station_type"):
            station.station_type = properties["station_type"]

        # Determine if station is active based on last year of data
        current_year = datetime.now().year
        if station.last_year and station.last_year < (current_year - 2):
            # Station hasn't reported data in over 2 years, mark as inactive
            station.is_active = False
            self.logger.info(
                f"Marked station {station.station_id} as inactive (last data: {station.last_year})"
            )

        station.update_timestamp()
