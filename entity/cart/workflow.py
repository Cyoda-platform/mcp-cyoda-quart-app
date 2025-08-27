import asyncio, datetime, uuid, logging
from common.config.config import ENTITY_VERSION
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

async def is_cart_not_empty(entity: dict) -> bool:
    try:
        lines = entity.get("lines", [])
        return bool(lines) and sum(line.get("qty", 0) for line in lines) > 0
    except Exception as e:
        logger.exception(e)
        return False

async def is_cart_status_active(entity: dict) -> bool:
    try:
        return entity.get("status") == "ACTIVE"
    except Exception as e:
        logger.exception(e)
        return False

async def is_cart_status_checking_out(entity: dict) -> bool:
    try:
        return entity.get("status") == "CHECKING_OUT"
    except Exception as e:
        logger.exception(e)
        return False

async def is_cart_status_new(entity: dict) -> bool:
    try:
        return entity.get("status") == "NEW"
    except Exception as e:
        logger.exception(e)
        return False

async def order_created_successfully(entity: dict) -> bool:
    try:
        # Assuming entity has attribute to indicate order created success
        return entity.get("orderCreated") is True
    except Exception as e:
        logger.exception(e)
        return False

async def set_cart_status_checking_out(entity: dict):
    try:
        entity["status"] = "CHECKING_OUT"
        entity["updatedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
    except Exception as e:
        logger.exception(e)

async def set_cart_status_converted(entity: dict):
    try:
        entity["status"] = "CONVERTED"
        entity["updatedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
    except Exception as e:
        logger.exception(e)

async def set_cart_status_active(entity: dict):
    try:
        entity["status"] = "ACTIVE"
        entity["updatedAt"] = datetime.datetime.utcnow().isoformat() + "Z"
    except Exception as e:
        logger.exception(e)
