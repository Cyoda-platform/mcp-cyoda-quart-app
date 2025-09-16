"""
CatFact Retrieval Processor for retrieving cat facts from external API.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from application.entity.catfact.version_1.catfact import CatFact
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)

CAT_FACT_API_URL = "https://catfact.ninja/fact"


class CatFactRetrievalProcessor(CyodaProcessor):
    """Processor to retrieve cat facts from external API."""

    def __init__(self, name: str = "CatFactRetrievalProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Retrieves cat fact from external API"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Retrieve cat fact from external API."""
        try:
            if not isinstance(entity, CatFact):
                raise ProcessorError(
                    self.name, f"Expected CatFact entity, got {type(entity)}"
                )

            # Call Cat Fact API
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(CAT_FACT_API_URL)
                response.raise_for_status()
                data = response.json()

            # Extract fact data
            fact_text = data.get("fact")
            if not fact_text:
                raise ProcessorError(self.name, "No fact received from API")

            # Update entity with fact data
            entity.fact = fact_text
            entity.length = data.get("length", len(fact_text))
            entity.apiFactId = data.get("id")  # May be None
            entity.retrievedDate = datetime.now(timezone.utc)

            logger.info(f"Retrieved cat fact: {fact_text[:50]}...")
            return entity

        except httpx.HTTPError as e:
            logger.exception(f"HTTP error retrieving cat fact: {e}")
            raise ProcessorError(
                self.name, f"Failed to retrieve cat fact from API: {str(e)}", e
            )
        except Exception as e:
            logger.exception(
                f"Failed to retrieve cat fact for entity {entity.entity_id}"
            )
            raise ProcessorError(self.name, f"Failed to retrieve cat fact: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, CatFact)
