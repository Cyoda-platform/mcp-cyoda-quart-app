import asyncio
import logging
import httpx
from datetime import datetime
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"

async def start_ingestion(entity: dict):
    entity["state"] = "INGESTING"
    entity["started_at"] = datetime.utcnow().isoformat()
    entity["completed_at"] = None
    entity["error_message"] = None
    return entity

async def fetch_and_process_data(entity: dict):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(NOBEL_API_URL)
            resp.raise_for_status()
            data = resp.json()
        records = data.get("records", [])
        valid_laureates = []
        for rec in records:
            laureate = validate_laureate(rec)
            if laureate:
                valid_laureates.append(laureate)
        for laureate in valid_laureates:
            try:
                await entity_service.update_item(
                    token=cyoda_auth_service,
                    entity_model="laureate",
                    entity_version=ENTITY_VERSION,
                    entity=laureate,
                    technical_id=str(laureate["id"]),
                    meta={}
                )
            except Exception as e:
                logger.exception(f"Failed to update laureate id={laureate['id']}: {e}")
        entity["state"] = "SUCCEEDED"
        entity["completed_at"] = datetime.utcnow().isoformat()
        entity["error_message"] = None
    except Exception as e:
        logger.exception(e)
        entity["state"] = "FAILED"
        entity["completed_at"] = datetime.utcnow().isoformat()
        entity["error_message"] = str(e)
    return entity

async def notify_subscribers(entity: dict):
    try:
        subscribers = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
        )
        notify_payload = {
            "job_id": entity.get("job_id"),
            "status": entity.get("state"),
            "error": entity.get("error_message"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        async def notify(sub):
            try:
                if sub.get("email"):
                    logger.info(f"Notify email {sub['email']}: {notify_payload}")
                if sub.get("webhook_url"):
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(sub["webhook_url"], json=notify_payload, timeout=10)
                        resp.raise_for_status()
                    logger.info(f"Notify webhook {sub['webhook_url']} succeeded")
            except Exception as e:
                logger.exception(f"Notification failed for subscriber {sub.get('subscriber_id')}: {e}")
        await asyncio.gather(*(notify(sub) for sub in subscribers))
        entity["state"] = "NOTIFIED_SUBSCRIBERS"
    except Exception as e:
        logger.exception(f"Failed to notify subscribers: {e}")
        entity.setdefault("notification_error", str(e))
    return entity

def is_succeeded(entity: dict) -> bool:
    return entity.get("state") == "SUCCEEDED"

def is_failed(entity: dict) -> bool:
    return entity.get("state") == "FAILED"

def validate_laureate(raw: dict) -> dict:
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