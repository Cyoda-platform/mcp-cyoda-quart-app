"""
CatFactRetrievalProcessor for Cyoda Client Application

Retrieves cat fact from external API and stores it.
Handles API calls with retry logic and error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional, cast

import httpx

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CatFactRetrievalProcessor(CyodaProcessor):
    """
    Processor for retrieving cat facts from external API.
    Handles API calls with retry logic and creates CatFact entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactRetrievalProcessor",
            description="Retrieves cat fact from external API and stores it",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )
        self.api_url = "https://catfact.ninja/fact"
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact retrieval according to functional requirements.

        Args:
            entity: The CatFact entity to populate (can be empty)
            **kwargs: Additional processing parameters

        Returns:
            The CatFact entity populated with retrieved data
        """
        try:
            self.logger.info(
                f"Processing cat fact retrieval {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Retrieve cat fact from external API
            fact_data = await self._retrieve_cat_fact_with_retry()

            # Populate the entity with retrieved data
            cat_fact.fact_text = fact_data["fact"]
            cat_fact.fact_length = len(fact_data["fact"])
            cat_fact.retrieved_date = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            cat_fact.external_fact_id = fact_data.get("id")

            # Update timestamp
            cat_fact.update_timestamp()

            # Log retrieval event
            self.logger.info(
                f"Cat fact retrieved successfully: {cat_fact.fact_text[:50]}..."
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error processing cat fact retrieval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _retrieve_cat_fact_with_retry(self) -> dict[str, Any]:
        """
        Retrieve cat fact from API with exponential backoff retry logic.

        Returns:
            Dictionary containing fact data from API

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                self.logger.info(
                    f"Attempting to retrieve cat fact (attempt {attempt + 1}/{self.max_retries})"
                )

                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(self.api_url)
                    response.raise_for_status()

                    fact_data = response.json()

                    # Validate response structure
                    if not isinstance(fact_data, dict) or "fact" not in fact_data:
                        raise ValueError("Invalid response format from Cat Fact API")

                    if not fact_data["fact"] or len(fact_data["fact"].strip()) < 10:
                        raise ValueError("Retrieved fact is too short or empty")

                    self.logger.info("Cat fact retrieved successfully from API")
                    return fact_data

            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Cat fact retrieval attempt {attempt + 1} failed: {str(e)}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2**attempt)
                    self.logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)

        # All retries failed
        error_msg = f"Failed to retrieve cat fact after {self.max_retries} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"

        self.logger.error(error_msg)
        raise Exception(error_msg)
