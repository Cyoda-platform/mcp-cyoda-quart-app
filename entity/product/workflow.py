import asyncio, datetime, uuid, ulid, logging
from common.config.config import ENTITY_VERSION
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = None, None

async def needs_user_id(entity: dict) -> bool:
    try:
        return not bool(entity.get("userId"))
    except Exception as e:
        logger.exception(e)
        return False

async def has_user_id(entity: dict) -> bool:
    try:
        return bool(entity.get("userId"))
    except Exception as e:
        logger.exception(e)
        return False

async def process_user(entity: dict):
    global entity_service, cyoda_auth_service
    try:
        if entity_service is None or cyoda_auth_service is None:
            entity_service, cyoda_auth_service = get_services()
        if not entity.get("userId"):
            entity["userId"] = str(uuid.uuid4())
    except Exception as e:
        logger.exception(e)
    return entity