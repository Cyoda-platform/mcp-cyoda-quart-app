"""
Fetch and Process Data Processor for Nobel laureate data ingestion.
"""
import logging
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from entity.cyoda_entity import CyodaEntity
from entity.job import JobEntity
from common.config.config import ENTITY_VERSION
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)

# Nobel API URL
NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"


class FetchAndProcessDataProcessor(CyodaProcessor):
    """Processor to fetch and process Nobel laureate data."""
    
    def __init__(self, name: str = "fetch_and_process_data", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Fetches Nobel laureate data from API and processes it"
        )
    
    async def process(self, entity: CyodaEntity, payload: Optional[Dict[str, Any]] = None, **kwargs) -> CyodaEntity:
        """Fetch and process Nobel laureate data."""
        try:
            # Get services
            entity_service, cyoda_auth_service = self._get_services()
            
            # Fetch data from Nobel API
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(NOBEL_API_URL)
                resp.raise_for_status()
                data = resp.json()
            
            records = data.get("records", [])
            valid_laureates = []
            
            # Validate and process each laureate
            for rec in records:
                laureate_data = self._validate_laureate(rec)
                if laureate_data:
                    valid_laureates.append(laureate_data)
            
            # Save laureates to the system
            for laureate_data in valid_laureates:
                try:
                    await entity_service.update_item(
                        token=cyoda_auth_service,
                        entity_model="laureate",
                        entity_version=ENTITY_VERSION,
                        entity=laureate_data,
                        technical_id=str(laureate_data["id"]),
                        meta={}
                    )
                except Exception as e:
                    logger.exception(f"Failed to update laureate id={laureate_data['id']}: {e}")
            
            # Update entity state
            entity.set_state("SUCCEEDED")
            entity.add_metadata("completed_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("error_message", None)
            entity.add_metadata("processed_laureates", len(valid_laureates))
            
            logger.info(f"Successfully processed {len(valid_laureates)} laureates for job {entity.entity_id}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to fetch and process data for job {entity.entity_id}")
            entity.set_state("FAILED")
            entity.add_metadata("completed_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("error_message", str(e))
            raise ProcessorError(self.name, f"Failed to fetch and process data: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, JobEntity) or entity.get_metadata("entity_type") == "job"
    
    def _get_services(self):
        """Get entity service and auth service."""
        from service.services import get_entity_service, get_auth_service
        return get_entity_service(), get_auth_service()
    
    def _validate_laureate(self, raw: dict) -> Optional[dict]:
        """Validate and extract laureate data from raw API response."""
        fields = raw.get("record", {}).get("fields", {})
        required = [
            "id", "firstname", "surname", "gender", "born", "borncountry",
            "borncountrycode", "borncity", "year", "category", "motivation",
            "name", "city", "country",
        ]
        
        for f in required:
            if fields.get(f) is None:
                logger.warning(f"Missing required laureate field: {f}")
                return None
        
        born = fields.get("born")
        died = fields.get("died")
        
        try:
            if born:
                datetime.fromisoformat(born)
            if died:
                datetime.fromisoformat(died)
        except Exception:
            logger.warning(f"Invalid date format for laureate id={fields.get('id')}")
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
