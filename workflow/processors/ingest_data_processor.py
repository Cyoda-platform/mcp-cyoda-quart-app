"""
Ingest Data Processor for Nobel laureate data ingestion.
"""
import logging
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from entity.job import JobEntity
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)

# Nobel API URL
NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"


class IngestDataProcessor(CyodaProcessor):
    """Processor to ingest Nobel laureate data."""
    
    def __init__(self, name: str = "ingest_data", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Ingests Nobel laureate data from external API"
        )
    
    async def process(self, entity: CyodaEntity, payload: Optional[Dict[str, Any]] = None, **kwargs) -> CyodaEntity:
        """Ingest Nobel laureate data."""
        try:
            entity.set_state('INGESTING')
            entity.add_metadata("ingestion_started", datetime.now(timezone.utc).isoformat())
            
            # Fetch data from Nobel API
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(NOBEL_API_URL)
                resp.raise_for_status()
                data = resp.json()
            
            records = data.get("records", [])
            valid_laureates = []
            
            # Process each record
            for rec in records:
                laureate = await self._process_laureate_record(rec)
                if laureate:
                    valid_laureates.append(laureate)
            
            # Update entity with results
            entity.set_state('SUCCEEDED')
            entity.add_metadata('laureates', valid_laureates)
            entity.add_metadata('completed_at', datetime.now(timezone.utc).isoformat())
            entity.add_metadata('error_message', None)
            entity.add_metadata('processed_count', len(valid_laureates))
            
            logger.info(f"Successfully ingested {len(valid_laureates)} laureates for entity {entity.entity_id}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to ingest data for entity {entity.entity_id}")
            entity.set_state('FAILED')
            entity.add_metadata('completed_at', datetime.now(timezone.utc).isoformat())
            entity.add_metadata('error_message', str(e))
            raise ProcessorError(self.name, f"Failed to ingest data: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return True  # This processor can work with any entity type
    
    async def _process_laureate_record(self, raw: dict) -> Optional[dict]:
        """Process a single laureate record from the API."""
        try:
            fields = raw.get("record", {}).get("fields", {})
            required = [
                "id", "firstname", "surname", "gender", "born", "borncountry",
                "borncountrycode", "borncity", "year", "category", "motivation",
                "name", "city", "country"
            ]
            
            # Check for required fields
            for f in required:
                if fields.get(f) is None:
                    return None
            
            born = fields.get("born")
            died = fields.get("died")
            
            # Validate date formats
            if born:
                try:
                    datetime.fromisoformat(born)
                except ValueError:
                    return None
            if died:
                try:
                    datetime.fromisoformat(died)
                except ValueError:
                    return None
            
            return {
                "id": fields["id"],
                "firstname": fields["firstname"],
                "surname": fields["surname"],
                "gender": fields["gender"],
                "born": born,
                "died": died,
                "borncountry": fields["borncountry"],
                "borncountrycode": fields["borncountrycode"],
                "borncity": fields["borncity"],
                "year": fields["year"],
                "category": fields["category"],
                "motivation": fields["motivation"],
                "name": fields["name"],
                "city": fields["city"],
                "country": fields["country"],
            }
            
        except Exception as e:
            logger.exception(f"Failed to process laureate record: {e}")
            return None
