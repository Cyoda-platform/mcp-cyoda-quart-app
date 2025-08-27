import asyncio
import datetime
import uuid
import ulid
import logging
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def gen_id():
    return str(uuid.uuid4())

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

async def process_pickledger(entity: dict):
    try:
        if not entity.get('pickId'):
            entity['pickId'] = gen_id()
    except Exception as e:
        logger.exception(e)
    return entity

async def guard_pick_complete(entity: dict) -> bool:
    try:
        # Example condition: assume entity has 'delta' and 'note' or 'actor' for audit
        delta = entity.get('delta', 0)
        audited = bool(entity.get('note')) or bool(entity.get('actor'))
        return delta != 0 and audited
    except Exception as e:
        logger.exception(e)
        return False

async def guard_not_pick_complete(entity: dict) -> bool:
    try:
        delta = entity.get('delta', 0)
        audited = bool(entity.get('note')) or bool(entity.get('actor'))
        return not (delta != 0 and audited)
    except Exception as e:
        logger.exception(e)
        return False

async def guard_pick_audited(entity: dict) -> bool:
    try:
        return bool(entity.get('note')) or bool(entity.get('actor'))
    except Exception as e:
        logger.exception(e)
        return False

async def guard_not_pick_audited(entity: dict) -> bool:
    try:
        return not (bool(entity.get('note')) or bool(entity.get('actor')))
    except Exception as e:
        logger.exception(e)
        return False