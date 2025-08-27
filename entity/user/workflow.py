import asyncio
import datetime
import uuid
import ulid
import logging
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

async def process_user(entity: dict):
    try:
        if not entity.get('userId'):
            entity['userId'] = str(uuid.uuid4())
    except Exception as e:
        logger.exception(e)
    return entity

async def needs_user_id(entity: dict) -> bool:
    try:
        return not bool(entity.get('userId'))
    except Exception as e:
        logger.exception(e)
        return False

async def has_user_id(entity: dict) -> bool:
    try:
        return bool(entity.get('userId'))
    except Exception as e:
        logger.exception(e)
        return False