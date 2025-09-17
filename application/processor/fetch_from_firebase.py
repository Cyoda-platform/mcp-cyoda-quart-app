"""
FetchFromFirebaseProcessor for Cyoda Client Application

Fetches items from Firebase HN API as specified in workflow requirements.
"""

import logging
from typing import Any, Dict, List

import httpx

from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class FetchFromFirebaseProcessor(CyodaProcessor):
    """
    Processor for fetching items from Firebase HN API.

    Calls Firebase API, retrieves items, and populates collection.
    """

    def __init__(self) -> None:
        super().__init__(
            name="fetch_from_firebase", description="Fetches items from Firebase HN API"
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        self.firebase_base_url = "https://hacker-news.firebaseio.com/v0"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Fetch items from Firebase HN API according to functional requirements.

        Args:
            entity: The HNItemCollection with API parameters
            **kwargs: Additional processing parameters

        Returns:
            Collection populated with fetched items
        """
        try:
            self.logger.info(
                f"Fetching from Firebase for HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Get API parameters from metadata
            api_endpoint = (
                collection.metadata.get("api_endpoint", "topstories")
                if collection.metadata
                else "topstories"
            )
            limit = collection.metadata.get("limit", 50) if collection.metadata else 50

            # Fetch items from Firebase API
            items = await self._fetch_items_from_api(api_endpoint, limit)

            if items:
                # Add items to collection
                collection.add_items(items)

                # Update metadata
                if not collection.metadata:
                    collection.metadata = {}
                collection.metadata["firebase_fetch_completed"] = True
                collection.metadata["api_endpoint_used"] = api_endpoint
                collection.metadata["items_fetched"] = len(items)

                self.logger.info(
                    f"Successfully fetched {len(items)} items from Firebase API endpoint '{api_endpoint}'"
                )
            else:
                self.logger.warning(
                    f"No items fetched from Firebase API endpoint '{api_endpoint}'"
                )

            return collection

        except Exception as e:
            self.logger.error(
                f"Error fetching from Firebase for HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _fetch_items_from_api(
        self, endpoint: str, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch items from Firebase HN API.

        Args:
            endpoint: API endpoint (topstories, newstories, beststories, etc.)
            limit: Maximum number of items to fetch

        Returns:
            List of item dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, get the list of item IDs
                ids_url = f"{self.firebase_base_url}/{endpoint}.json"
                self.logger.info(f"Fetching item IDs from: {ids_url}")

                ids_response = await client.get(ids_url)
                ids_response.raise_for_status()

                item_ids = ids_response.json()
                if not item_ids:
                    self.logger.warning(f"No item IDs returned from {endpoint}")
                    return []

                # Limit the number of items to fetch
                item_ids = item_ids[:limit]

                self.logger.info(f"Fetching details for {len(item_ids)} items")

                # Fetch details for each item
                items = []
                for item_id in item_ids:
                    try:
                        item_url = f"{self.firebase_base_url}/item/{item_id}.json"
                        item_response = await client.get(item_url)
                        item_response.raise_for_status()

                        item_data = item_response.json()
                        if item_data:
                            items.append(item_data)
                        else:
                            self.logger.warning(f"No data returned for item {item_id}")

                    except Exception as item_error:
                        self.logger.error(
                            f"Error fetching item {item_id}: {str(item_error)}"
                        )
                        continue

                self.logger.info(
                    f"Successfully fetched {len(items)} items from Firebase API"
                )
                return items

        except httpx.HTTPError as http_error:
            self.logger.error(
                f"HTTP error fetching from Firebase API: {str(http_error)}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Error fetching from Firebase API: {str(e)}")
            raise

    def _get_available_endpoints(self) -> List[str]:
        """Get list of available Firebase HN API endpoints"""
        return [
            "topstories",
            "newstories",
            "beststories",
            "askstories",
            "showstories",
            "jobstories",
        ]
