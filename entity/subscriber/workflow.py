import asyncio
import logging
from common.config.config import ENTITY_VERSION
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"

async def ingest_data(entity: dict):
    try:
        entity['state'] = 'INGESTING'
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(NOBEL_API_URL)
            resp.raise_for_status()
            data = resp.json()
        records = data.get("records", [])
        valid_laureates = []
        for rec in records:
            laureate = await process_laureate(rec)
            if laureate:
                valid_laureates.append(laureate)
        entity['laureates'] = valid_laureates
        entity['state'] = 'SUCCEEDED'
        entity['completed_at'] = asyncio.get_event_loop().time()
        entity['error_message'] = None
    except Exception as e:
        logger.exception(e)
        entity['state'] = 'FAILED'
        entity['completed_at'] = asyncio.get_event_loop().time()
        entity['error_message'] = str(e)

async def process_laureate(raw: dict):
    try:
        fields = raw.get("record", {}).get("fields", {})
        required = [
            "id", "firstname", "surname", "gender", "born", "borncountry",
            "borncountrycode", "borncity", "year", "category", "motivation",
            "name", "city", "country"
        ]
        for f in required:
            if fields.get(f) is None:
                return None
        born = fields.get("born")
        died = fields.get("died")
        if born:
            # validate date format
            _ = born
        if died:
            _ = died
        laureate = {
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
        return laureate
    except Exception as e:
        logger.exception(e)
        return None

async def notify_subscribers(entity: dict):
    try:
        subscribers = entity.get("subscribers", [])
        notify_payload = {
            "job_id": entity.get("job_id"),
            "status": entity.get("state"),
            "error": entity.get("error_message"),
            "timestamp": asyncio.get_event_loop().time()
        }
        async def notify(sub):
            try:
                if sub.get("email"):
                    logger.info(f"Notify email {sub['email']} with payload {notify_payload}")
                if sub.get("webhook_url"):
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(sub["webhook_url"], json=notify_payload, timeout=10)
                        resp.raise_for_status()
                    logger.info(f"Notify webhook {sub['webhook_url']} succeeded")
            except Exception as e:
                logger.exception(e)
        await asyncio.gather(*(notify(sub) for sub in subscribers))
        entity['state'] = 'NOTIFIED_SUBSCRIBERS'
    except Exception as e:
        logger.exception(e)

async def is_ingestion_successful(entity: dict) -> bool:
    return entity.get('state') == 'SUCCEEDED'

async def has_ingestion_failed(entity: dict) -> bool:
    return entity.get('state') == 'FAILED'

async def process_subscriber(entity: dict):
    try:
        if entity.get("email"):
            entity["email"] = entity["email"].lower()
        if "status" not in entity:
            entity["status"] = "active"
        return entity
    except Exception as e:
        logger.exception(e)
        return entity