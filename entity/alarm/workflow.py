from datetime import datetime, timedelta
import uuid
import asyncio
import logging
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

COOKING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

async def alarm_countdown(alarm_id: str):
    try:
        # TODO: Implement countdown logic that updates entity status to finished when time expires
        pass
    except Exception as e:
        logger.exception(e)

async def init_alarm(entity: dict):
    try:
        if "id" not in entity or not entity["id"]:
            entity["id"] = str(uuid.uuid4())

        egg_type = entity.get("egg_type")
        if not isinstance(egg_type, str) or egg_type not in COOKING_TIMES:
            raise ValueError(f"Invalid egg_type '{egg_type}'")

        now = datetime.utcnow()
        duration = COOKING_TIMES[egg_type]

        entity["status"] = "running"
        entity["requested_at"] = now.isoformat()
        entity["end_time"] = (now + timedelta(seconds=duration)).isoformat()

        asyncio.create_task(alarm_countdown(entity["id"]))

    except Exception as e:
        logger.exception(e)
        raise
    return entity

async def can_start(entity: dict) -> bool:
    try:
        return entity.get("status") == "none" and isinstance(entity.get("egg_type"), str) and entity["egg_type"] in COOKING_TIMES
    except Exception as e:
        logger.exception(e)
        return False

async def can_finish(entity: dict) -> bool:
    try:
        return entity.get("status") == "running"
    except Exception as e:
        logger.exception(e)
        return False

async def can_cancel(entity: dict) -> bool:
    try:
        return entity.get("status") in ("none", "running")
    except Exception as e:
        logger.exception(e)
        return False